from prometheus_client import Gauge, Counter, Histogram
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class ChatMetricsCollector:
    """Collector for chat-related metrics"""

    def __init__(self, db_pool):
        self.db_pool = db_pool

        # Chat counts
        self.total_chats = Gauge('openwebui_chats_total', 'Total number of chats')
        self.total_chats_by_model = Gauge('openwebui_chats_by_model', 'Number of chats by model',
                               ['model_name'])
        self.archived_chats = Gauge('openwebui_chats_archived', 'Number of archived chats',
                                  ['model_name'])
        self.pinned_chats = Gauge('openwebui_chats_pinned', 'Number of pinned chats',
                                ['model_name'])

        # Chat metrics by user
        self.chats_by_user = Gauge('openwebui_chats_by_user',
                                 'Number of chats per user',
                                 ['user_id', 'user_name', 'user_email', 'model_name'])

        # Shared chats
        self.shared_chats = Gauge('openwebui_chats_shared', 'Number of shared chats')

        # Chat activity
        self.messages_by_model = Gauge('openwebui_messages_by_model',
                                'Number of messages by model',
                                ['model_name'])

        # Total messages across all chats
        self.messages_total = Gauge('openwebui_messages_total', 'Total number of messages across all chats')

        # Start collecting metrics
        self.collect_metrics()

    def collect_metrics(self):
        """Collect all chat-related metrics"""
        try:
            with self.db_pool.get_connection() as cur:
                # Total chats (all)
                cur.execute("SELECT COUNT(*) FROM public.chat")
                self.total_chats.set(cur.fetchone()[0])

                # Total chats by model
                cur.execute("""
                    WITH chat_models AS (
                        SELECT DISTINCT
                            c.id,
                            json_array_elements(c.chat->'messages')::jsonb->>'model' as model_name
                        FROM public.chat c
                        WHERE c.chat->'messages' IS NOT NULL
                    )
                    SELECT
                        model_name,
                        COUNT(DISTINCT id)
                    FROM chat_models
                    WHERE model_name IS NOT NULL
                    GROUP BY model_name
                """)
                for model_name, count in cur.fetchall():
                    self.total_chats_by_model.labels(model_name=model_name).set(count)


                # Archived chats by model
                cur.execute("""
                    WITH chat_models AS (
                        SELECT DISTINCT
                            c.id,
                            json_array_elements(c.chat->'messages')::jsonb->>'model' as model_name
                        FROM public.chat c
                        WHERE c.chat->'messages' IS NOT NULL
                        AND c.archived = true
                    )
                    SELECT
                        model_name,
                        COUNT(DISTINCT id)
                    FROM chat_models
                    WHERE model_name IS NOT NULL
                    GROUP BY model_name
                """)
                for model_name, count in cur.fetchall():
                    self.archived_chats.labels(model_name=model_name).set(count)

                # Pinned chats by model
                cur.execute("""
                    WITH chat_models AS (
                        SELECT DISTINCT
                            c.id,
                            json_array_elements(c.chat->'messages')::jsonb->>'model' as model_name
                        FROM public.chat c
                        WHERE c.chat->'messages' IS NOT NULL
                        AND c.pinned = true
                    )
                    SELECT
                        model_name,
                        COUNT(DISTINCT id)
                    FROM chat_models
                    WHERE model_name IS NOT NULL
                    GROUP BY model_name
                """)
                for model_name, count in cur.fetchall():
                    self.pinned_chats.labels(model_name=model_name).set(count)

                # Debug: Print the SQL query and results
                debug_query = """
                    SELECT DISTINCT
                        c.user_id,
                        u.name,
                        u.email,
                        json_array_elements(c.chat->'messages')::jsonb->>'model' as model_name,
                        COUNT(DISTINCT c.id) as chat_count
                    FROM public.chat c
                    JOIN public.user u ON c.user_id = u.id
                    WHERE c.chat->'messages' IS NOT NULL
                    GROUP BY c.user_id, u.name, u.email, model_name
                """
                cur.execute(debug_query)
                results = cur.fetchall()
                logger.info("Debug - Query results:")
                for row in results:
                    logger.info(f"User: {row[0]}, Name: {row[1]}, Email: {row[2]}, Model: {row[3]}, Count: {row[4]}")
                    self.chats_by_user.labels(
                        user_id=row[0],
                        user_name=row[1],
                        user_email=row[2],
                        model_name=row[3]
                    ).set(row[4])

                # Shared chats
                cur.execute("SELECT COUNT(*) FROM public.chat WHERE share_id IS NOT NULL")
                self.shared_chats.set(cur.fetchone()[0])

                # Message count by model
                cur.execute("""
                    WITH message_models AS (
                        SELECT
                            json_array_elements(c.chat->'messages')::jsonb->>'model' as model_name
                        FROM public.chat c
                        WHERE c.chat->'messages' IS NOT NULL
                    )
                    SELECT
                        model_name,
                        COUNT(*) as message_count
                    FROM message_models
                    WHERE model_name IS NOT NULL
                    GROUP BY model_name
                """)
                for model_name, count in cur.fetchall():
                    self.messages_by_model.labels(model_name=model_name).set(count)
                    logger.info(f"Messages for model {model_name}: {count}")

                # Total messages across all chats - calculate from the sum of messages by model
                # This ensures consistency between the two metrics
                total_messages = 0

                # First, get the count of messages with models
                cur.execute("""
                    WITH message_models AS (
                        SELECT
                            json_array_elements(c.chat->'messages')::jsonb->>'model' as model_name
                        FROM public.chat c
                        WHERE c.chat->'messages' IS NOT NULL
                    )
                    SELECT
                        SUM(message_count) as total_count
                    FROM (
                        SELECT
                            model_name,
                            COUNT(*) as message_count
                        FROM message_models
                        GROUP BY model_name
                    ) as model_counts
                """)
                result = cur.fetchone()
                if result and result[0]:
                    total_messages = result[0]

                # Set the metric
                self.messages_total.set(total_messages)
                logger.info(f"Total messages count: {total_messages}")

        except Exception as e:
            logger.error(f"Error collecting chat metrics: {e}")
