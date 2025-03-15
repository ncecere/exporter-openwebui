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
                            json_array_elements(c.chat->'messages')->>'model' as model_name
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
                            json_array_elements(c.chat->'messages')->>'model' as model_name
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
                            json_array_elements(c.chat->'messages')->>'model' as model_name
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
                        json_array_elements(c.chat->'messages')->>'model' as model_name,
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

                # Message count by model - handle both array and object formats
                try:
                    # First try counting messages by model in the messages array
                    cur.execute("""
                        WITH array_messages AS (
                            SELECT
                                json_array_elements(c.chat->'messages')->>'model' as model_name
                            FROM public.chat c
                            WHERE c.chat->'messages' IS NOT NULL AND jsonb_typeof(c.chat->'messages') = 'array'
                        ),
                        object_messages AS (
                            SELECT
                                value->>'model' as model_name
                            FROM public.chat c,
                            jsonb_each(c.chat->'history'->'messages') msg(key, value)
                            WHERE c.chat->'history'->'messages' IS NOT NULL AND jsonb_typeof(c.chat->'history'->'messages') = 'object'
                        ),
                        combined_messages AS (
                            SELECT model_name FROM array_messages
                            UNION ALL
                            SELECT model_name FROM object_messages
                        )
                        SELECT
                            model_name,
                            COUNT(*) as message_count
                        FROM combined_messages
                        WHERE model_name IS NOT NULL
                        GROUP BY model_name
                    """)

                    # Reset all existing metrics to avoid stale data
                    for model_name, count in cur.fetchall():
                        self.messages_by_model.labels(model_name=model_name).set(count)
                        logger.info(f"Messages for model {model_name}: {count}")
                except Exception as e:
                    logger.error(f"Error counting messages by model: {e}")

                # Total messages across all chats
                # The messages can be stored in different formats depending on the chat structure
                # Try both the array format and the object format
                try:
                    # First try counting messages in the messages array
                    cur.execute("""
                        SELECT COALESCE(SUM(jsonb_array_length(c.chat->'messages')), 0)
                        FROM public.chat c
                        WHERE c.chat->'messages' IS NOT NULL AND jsonb_typeof(c.chat->'messages') = 'array'
                    """)
                    array_count = cur.fetchone()[0] or 0

                    # Then try counting messages in the history.messages object
                    cur.execute("""
                        SELECT COALESCE(SUM(jsonb_object_length(c.chat->'history'->'messages')), 0)
                        FROM public.chat c
                        WHERE c.chat->'history'->'messages' IS NOT NULL AND jsonb_typeof(c.chat->'history'->'messages') = 'object'
                    """)
                    object_count = cur.fetchone()[0] or 0

                    # Set the total as the sum of both counts
                    total_messages = array_count + object_count
                    self.messages_total.set(total_messages)
                    logger.info(f"Total messages count: {total_messages} (array: {array_count}, object: {object_count})")
                except Exception as e:
                    logger.error(f"Error counting total messages: {e}")
                    self.messages_total.set(0)

        except Exception as e:
            logger.error(f"Error collecting chat metrics: {e}")
