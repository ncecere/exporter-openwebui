from prometheus_client import Gauge, Counter
import logging

logger = logging.getLogger(__name__)

class ModelMetricsCollector:
    """Collector for AI model, tool, and function related metrics"""

    def __init__(self, db):
        self.db = db

        # Model metrics
        self.total_models = Gauge('openwebui_models_total', 'Total number of models')
        self.active_models = Gauge('openwebui_models_active', 'Number of active models')
        self.models_by_user = Gauge('openwebui_models_by_user',
                                 'Number of models per user',
                                 ['user_id', 'user_name'])
        self.models_by_base = Gauge('openwebui_models_by_base',
                                 'Number of models by base model',
                                 ['base_model_id', 'model_name'])

        # Tool metrics
        self.total_tools = Gauge('openwebui_tools_total', 'Total number of tools')
        self.tools_by_user = Gauge('openwebui_tools_by_user',
                                'Number of tools per user',
                                ['user_id', 'user_name', 'tool_name'])

        # Function metrics
        self.total_functions = Gauge('openwebui_functions_total', 'Total number of functions')
        self.active_functions = Gauge('openwebui_functions_active',
                                   'Number of active functions')
        self.global_functions = Gauge('openwebui_functions_global',
                                   'Number of global functions')
        self.functions_by_type = Gauge('openwebui_functions_by_type',
                                    'Number of functions by type',
                                    ['type', 'function_name'])
        self.functions_by_user = Gauge('openwebui_functions_by_user',
                                    'Number of functions per user',
                                    ['user_id', 'user_name', 'function_name'])

        # Start collecting metrics
        self.collect_metrics()

    def collect_metrics(self):
        """Collect all model-related metrics"""
        try:
            with self.db.cursor() as cur:
                # Model metrics
                cur.execute("SELECT COUNT(*) FROM public.model")
                self.total_models.set(cur.fetchone()[0])

                cur.execute("SELECT COUNT(*) FROM public.model WHERE is_active = true")
                self.active_models.set(cur.fetchone()[0])

                # Models by user with user names
                cur.execute("""
                    SELECT m.user_id, u.name, COUNT(*)
                    FROM public.model m
                    JOIN public.user u ON m.user_id = u.id
                    GROUP BY m.user_id, u.name
                """)
                for user_id, user_name, count in cur.fetchall():
                    self.models_by_user.labels(
                        user_id=user_id,
                        user_name=user_name
                    ).set(count)

                # Models by base model with names
                cur.execute("""
                    SELECT base_model_id, name, COUNT(*)
                    FROM public.model
                    WHERE base_model_id IS NOT NULL
                    GROUP BY base_model_id, name
                """)
                for base_model_id, model_name, count in cur.fetchall():
                    self.models_by_base.labels(
                        base_model_id=base_model_id,
                        model_name=model_name
                    ).set(count)

                # Tool metrics with names
                cur.execute("SELECT COUNT(*) FROM public.tool")
                self.total_tools.set(cur.fetchone()[0])

                cur.execute("""
                    SELECT t.user_id, u.name as user_name, t.name as tool_name, COUNT(*)
                    FROM public.tool t
                    JOIN public.user u ON t.user_id = u.id
                    GROUP BY t.user_id, u.name, t.name
                """)
                for user_id, user_name, tool_name, count in cur.fetchall():
                    self.tools_by_user.labels(
                        user_id=user_id,
                        user_name=user_name,
                        tool_name=tool_name
                    ).set(count)

                # Function metrics
                cur.execute("SELECT COUNT(*) FROM public.function")
                self.total_functions.set(cur.fetchone()[0])

                cur.execute("SELECT COUNT(*) FROM public.function WHERE is_active = true")
                self.active_functions.set(cur.fetchone()[0])

                cur.execute("SELECT COUNT(*) FROM public.function WHERE is_global = true")
                self.global_functions.set(cur.fetchone()[0])

                # Functions by type with names
                cur.execute("""
                    SELECT type, name, COUNT(*)
                    FROM public.function
                    GROUP BY type, name
                """)
                for func_type, function_name, count in cur.fetchall():
                    self.functions_by_type.labels(
                        type=func_type,
                        function_name=function_name
                    ).set(count)

                # Functions by user with names
                cur.execute("""
                    SELECT f.user_id, u.name as user_name, f.name as function_name, COUNT(*)
                    FROM public.function f
                    JOIN public.user u ON f.user_id = u.id
                    GROUP BY f.user_id, u.name, f.name
                """)
                for user_id, user_name, function_name, count in cur.fetchall():
                    self.functions_by_user.labels(
                        user_id=user_id,
                        user_name=user_name,
                        function_name=function_name
                    ).set(count)

        except Exception as e:
            logger.error(f"Error collecting model metrics: {e}")
