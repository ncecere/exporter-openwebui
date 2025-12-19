from prometheus_client import Gauge
import logging
import json
import gc
import time
from config import REQUEST_WINDOW_SECONDS

logger = logging.getLogger(__name__)

class ModelMetricsCollector:
    """Collector for AI model, tool, and function related metrics"""

    BATCH_SIZE = 50
    def __init__(self, db_pool):
        self.db_pool = db_pool

        # Model metrics
        self.total_models = Gauge('openwebui_models_total', 'Total number of base models')
        self.total_assistants = Gauge('openwebui_assistants_total', 'Total number of assistants')
        self.active_models = Gauge('openwebui_models_active', 'Number of active models')
        self.unique_model_users = Gauge('openwebui_model_unique_users',
                                    'Number of unique users that have used a model',
                                    ['model_name'])

        # Tool metrics
        self.total_tools = Gauge('openwebui_tools_total', 'Total number of tools')

        # Function metrics
        self.total_functions = Gauge('openwebui_functions_total', 'Total number of functions')
        self.active_functions = Gauge('openwebui_functions_active',
                                   'Number of active functions')
        self.global_functions = Gauge('openwebui_functions_global',
                                   'Number of global functions')

        # Start collecting metrics
        self.collect_metrics()

    def collect_metrics(self):
        """Collect all model-related metrics"""
        try:
            cutoff_epoch = int(time.time()) - int(REQUEST_WINDOW_SECONDS)
            with self.db_pool.get_connection() as cur:
                # Model metrics (base models where base_model_id is NULL)
                cur.execute("SELECT COUNT(*) FROM public.model WHERE base_model_id IS NULL")
                self.total_models.set(cur.fetchone()[0])

                # Assistant metrics (models where base_model_id is NOT NULL)
                cur.execute("SELECT COUNT(*) FROM public.model WHERE base_model_id IS NOT NULL")
                self.total_assistants.set(cur.fetchone()[0])

                cur.execute("SELECT COUNT(*) FROM public.model WHERE is_active = true")
                self.active_models.set(cur.fetchone()[0])

                # Unique users by model name (processed in Python to handle malformed entries)
                conn = cur.connection
                stream_cur = conn.cursor(name='model_metrics_stream')
                model_users = {}
                processed_rows = 0
                try:
                    stream_cur.itersize = self.BATCH_SIZE
                    stream_cur.execute(
                        """
                        SELECT user_id, chat
                        FROM public.chat
                        WHERE user_id IS NOT NULL
                          AND updated_at >= %s
                        """,
                        (cutoff_epoch,),
                    )
                    while True:
                        rows = stream_cur.fetchmany(self.BATCH_SIZE)
                        if not rows:
                            break

                        for user_id, chat_payload in rows:
                            if not user_id or chat_payload is None:
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

                            for message in messages:
                                if not isinstance(message, dict):
                                    continue
                                model_name = message.get('model')
                                if not isinstance(model_name, str):
                                    continue

                                cleaned_model = model_name.replace('\x00', '').strip()
                                if not cleaned_model:
                                    continue

                                users = model_users.setdefault(cleaned_model, set())
                                users.add(user_id)

                        processed_rows += len(rows)
                        if processed_rows and processed_rows % 1000 == 0:
                            logger.info(
                                "Processed %d chat rows for unique model users",
                                processed_rows,
                            )
                            gc.collect()
                finally:
                    stream_cur.close()

                self.unique_model_users.clear()
                for model_name, users in model_users.items():
                    self.unique_model_users.labels(model_name=model_name).set(len(users))

                logger.info(
                    "Completed unique model user aggregation: %d models scanned from %d chats",
                    len(model_users),
                    processed_rows,
                )


                # Tool metrics
                cur.execute("SELECT COUNT(*) FROM public.tool")
                self.total_tools.set(cur.fetchone()[0])

                # Function metrics
                cur.execute("SELECT COUNT(*) FROM public.function")
                self.total_functions.set(cur.fetchone()[0])

                cur.execute("SELECT COUNT(*) FROM public.function WHERE is_active = true")
                self.active_functions.set(cur.fetchone()[0])

                cur.execute("SELECT COUNT(*) FROM public.function WHERE is_global = true")
                self.global_functions.set(cur.fetchone()[0])

        except Exception as e:
            logger.error(f"Error collecting model metrics: {e}")
