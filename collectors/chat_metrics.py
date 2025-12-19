from prometheus_client import Gauge
import logging
import json
import gc
import time
from config import REQUEST_WINDOW_SECONDS

logger = logging.getLogger(__name__)

class ChatMetricsCollector:
    """Collector for chat-related metrics"""

    BATCH_SIZE = 50

    def __init__(self, db_pool):
        self.db_pool = db_pool

        # Chat counts
        self.total_chats = Gauge('openwebui_chats_total', 'Total number of chats')
        self.total_chats_by_model = Gauge('openwebui_chats_by_model',
                                          'Number of chats by model',
                                          ['model_name'])
        self.archived_chats = Gauge('openwebui_chats_archived',
                                    'Number of archived chats',
                                    ['model_name'])
        self.pinned_chats = Gauge('openwebui_chats_pinned',
                                  'Number of pinned chats',
                                  ['model_name'])

        # Shared chats
        self.shared_chats = Gauge('openwebui_chats_shared', 'Number of shared chats')

        # Chat activity
        self.messages_by_model = Gauge('openwebui_messages_by_model',
                                       'Number of messages by model',
                                       ['model_name'])

        # Total messages across all chats
        self.messages_total = Gauge('openwebui_messages_total',
                                    'Total number of messages across all chats')

        # Start collecting metrics
        self.collect_metrics()

    def collect_metrics(self):
        """Collect all chat-related metrics"""
        try:
            cutoff_epoch = int(time.time()) - int(REQUEST_WINDOW_SECONDS)
            with self.db_pool.get_connection() as cur:
                # Total chats (all)
                cur.execute("SELECT COUNT(*) FROM public.chat")
                self.total_chats.set(cur.fetchone()[0])

                # Model-level chat and message metrics (processed in Python to avoid encoding issues)
                conn = cur.connection
                stream_cur = conn.cursor(name='chat_metrics_stream')
                try:
                    stream_cur.itersize = self.BATCH_SIZE
                    stream_cur.execute("""
                        SELECT id, archived, pinned, chat
                        FROM public.chat
                        WHERE updated_at >= %s
                    """, (cutoff_epoch,))
                    model_chat_counts = {}
                    model_archived_counts = {}
                    model_pinned_counts = {}
                    model_message_counts = {}
                    total_messages = 0

                    processed_rows = 0
                    while True:
                        rows = stream_cur.fetchmany(self.BATCH_SIZE)
                        if not rows:
                            break

                        for chat_id, archived, pinned, chat_payload in rows:
                            if chat_payload is None:
                                continue

                            if isinstance(chat_payload, dict):
                                messages = chat_payload.get('messages') or []
                            else:
                                try:
                                    messages = json.loads(chat_payload).get('messages', [])
                                except (json.JSONDecodeError, AttributeError, TypeError):
                                    continue

                            if not isinstance(messages, list):
                                continue

                            total_messages += len(messages)

                            models_in_chat = set()
                            for message in messages:
                                if not isinstance(message, dict):
                                    continue
                                model_name = message.get('model')
                                if not isinstance(model_name, str):
                                    continue
                                cleaned_model = model_name.replace('\x00', '').strip()
                                if not cleaned_model:
                                    continue

                                models_in_chat.add(cleaned_model)
                                model_message_counts[cleaned_model] = model_message_counts.get(cleaned_model, 0) + 1

                            if not models_in_chat:
                                continue

                            for model in models_in_chat:
                                model_chat_counts[model] = model_chat_counts.get(model, 0) + 1
                                if archived:
                                    model_archived_counts[model] = model_archived_counts.get(model, 0) + 1
                                if pinned:
                                    model_pinned_counts[model] = model_pinned_counts.get(model, 0) + 1

                            del messages

                        processed_rows += len(rows)
                        if processed_rows and processed_rows % 1000 == 0:
                            logger.info("Processed %d chat rows for chat metrics", processed_rows)
                            gc.collect()
                finally:
                    stream_cur.close()

                # Clear existing label values to avoid stale metrics when models are removed
                self.total_chats_by_model.clear()
                self.archived_chats.clear()
                self.pinned_chats.clear()
                self.messages_by_model.clear()

                for model, chat_count in model_chat_counts.items():
                    self.total_chats_by_model.labels(model_name=model).set(chat_count)
                    archived_count = model_archived_counts.get(model, 0)
                    pinned_count = model_pinned_counts.get(model, 0)
                    message_count = model_message_counts.get(model, 0)

                    self.archived_chats.labels(model_name=model).set(archived_count)
                    self.pinned_chats.labels(model_name=model).set(pinned_count)
                    self.messages_by_model.labels(model_name=model).set(message_count)

                logger.info(
                    "Completed chat metrics aggregation: %d models across %d chats (total messages: %d)",
                    len(model_chat_counts),
                    processed_rows,
                    total_messages,
                )

                # Shared chats
                cur.execute("SELECT COUNT(*) FROM public.chat WHERE share_id IS NOT NULL")
                self.shared_chats.set(cur.fetchone()[0])

                # Total messages across all chats (regardless of whether a message has a model)
                self.messages_total.set(total_messages)

        except Exception as e:
            logger.error(f"Error collecting chat metrics: {e}")
