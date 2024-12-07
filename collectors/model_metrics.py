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
                                 ['user_id'])
        self.models_by_base = Gauge('openwebui_models_by_base',
                                 'Number of models by base model',
                                 ['base_model_id'])
        
        # Tool metrics
        self.total_tools = Gauge('openwebui_tools_total', 'Total number of tools')
        self.tools_by_user = Gauge('openwebui_tools_by_user',
                                'Number of tools per user',
                                ['user_id'])
        
        # Function metrics
        self.total_functions = Gauge('openwebui_functions_total', 'Total number of functions')
        self.active_functions = Gauge('openwebui_functions_active', 
                                   'Number of active functions')
        self.global_functions = Gauge('openwebui_functions_global',
                                   'Number of global functions')
        self.functions_by_type = Gauge('openwebui_functions_by_type',
                                    'Number of functions by type',
                                    ['type'])
        self.functions_by_user = Gauge('openwebui_functions_by_user',
                                    'Number of functions per user',
                                    ['user_id'])
        
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
                
                cur.execute("""
                    SELECT user_id, COUNT(*) 
                    FROM public.model 
                    GROUP BY user_id
                """)
                for user_id, count in cur.fetchall():
                    self.models_by_user.labels(user_id=user_id).set(count)
                
                cur.execute("""
                    SELECT base_model_id, COUNT(*) 
                    FROM public.model 
                    WHERE base_model_id IS NOT NULL 
                    GROUP BY base_model_id
                """)
                for base_model_id, count in cur.fetchall():
                    self.models_by_base.labels(base_model_id=base_model_id).set(count)
                
                # Tool metrics
                cur.execute("SELECT COUNT(*) FROM public.tool")
                self.total_tools.set(cur.fetchone()[0])
                
                cur.execute("""
                    SELECT user_id, COUNT(*) 
                    FROM public.tool 
                    GROUP BY user_id
                """)
                for user_id, count in cur.fetchall():
                    self.tools_by_user.labels(user_id=user_id).set(count)
                
                # Function metrics
                cur.execute("SELECT COUNT(*) FROM public.function")
                self.total_functions.set(cur.fetchone()[0])
                
                cur.execute("SELECT COUNT(*) FROM public.function WHERE is_active = true")
                self.active_functions.set(cur.fetchone()[0])
                
                cur.execute("SELECT COUNT(*) FROM public.function WHERE is_global = true")
                self.global_functions.set(cur.fetchone()[0])
                
                cur.execute("""
                    SELECT type, COUNT(*) 
                    FROM public.function 
                    GROUP BY type
                """)
                for func_type, count in cur.fetchall():
                    self.functions_by_type.labels(type=func_type).set(count)
                
                cur.execute("""
                    SELECT user_id, COUNT(*) 
                    FROM public.function 
                    GROUP BY user_id
                """)
                for user_id, count in cur.fetchall():
                    self.functions_by_user.labels(user_id=user_id).set(count)
                
        except Exception as e:
            logger.error(f"Error collecting model metrics: {e}")
