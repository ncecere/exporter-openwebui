from prometheus_client import Gauge, Counter
import logging

logger = logging.getLogger(__name__)

class ModelMetricsCollector:
    """Collector for AI model, tool, and function related metrics"""

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
        self.tools_by_user = Gauge('openwebui_tools_by_user',
                                'Number of tools per user',
                                ['user_id', 'user_name', 'user_email', 'tool_name'])

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
            with self.db_pool.get_connection() as cur:
                # Model metrics (base models where base_model_id is NULL)
                cur.execute("SELECT COUNT(*) FROM public.model WHERE base_model_id IS NULL")
                self.total_models.set(cur.fetchone()[0])

                # Assistant metrics (models where base_model_id is NOT NULL)
                cur.execute("SELECT COUNT(*) FROM public.model WHERE base_model_id IS NOT NULL")
                self.total_assistants.set(cur.fetchone()[0])

                cur.execute("SELECT COUNT(*) FROM public.model WHERE is_active = true")
                self.active_models.set(cur.fetchone()[0])

                # Unique users by model name (based on actual usage in chats)
                cur.execute("""
                    WITH chat_models AS (
                        SELECT DISTINCT
                            c.user_id,
                            json_array_elements(c.chat->'messages')->>'model' as model_name
                        FROM public.chat c
                        WHERE c.chat->'messages' IS NOT NULL
                    )
                    SELECT
                        model_name,
                        COUNT(DISTINCT user_id) as unique_users
                    FROM chat_models
                    WHERE model_name IS NOT NULL
                    GROUP BY model_name
                """)
                for model_name, unique_users in cur.fetchall():
                    self.unique_model_users.labels(
                        model_name=model_name
                    ).set(unique_users)


                # Debug: Tool metrics with names and emails
                debug_query = """
                    SELECT t.user_id, u.name, u.email, t.name, COUNT(*)
                    FROM public.tool t
                    JOIN public.user u ON t.user_id = u.id
                    GROUP BY t.user_id, u.name, u.email, t.name
                """
                cur.execute(debug_query)
                results = cur.fetchall()
                logger.info("Debug - Tools by user:")
                for row in results:
                    logger.info(f"User: {row[0]}, Name: {row[1]}, Email: {row[2]}, Tool: {row[3]}, Count: {row[4]}")
                    self.tools_by_user.labels(
                        user_id=row[0],
                        user_name=row[1],
                        user_email=row[2],
                        tool_name=row[3]
                    ).set(row[4])

                # Function metrics
                cur.execute("SELECT COUNT(*) FROM public.function")
                self.total_functions.set(cur.fetchone()[0])

                cur.execute("SELECT COUNT(*) FROM public.function WHERE is_active = true")
                self.active_functions.set(cur.fetchone()[0])

                cur.execute("SELECT COUNT(*) FROM public.function WHERE is_global = true")
                self.global_functions.set(cur.fetchone()[0])

        except Exception as e:
            logger.error(f"Error collecting model metrics: {e}")
