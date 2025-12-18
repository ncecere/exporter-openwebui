from prometheus_client import Gauge
import logging

logger = logging.getLogger(__name__)

class SystemMetricsCollector:
    """Collector for system-level metrics"""

    def __init__(self, db_pool):
        self.db_pool = db_pool

        # Configuration metrics
        self.config_version = Gauge('openwebui_config_version', 'Current configuration version')
        self.config_update_time = Gauge('openwebui_config_last_update',
                                     'Timestamp of last configuration update')

        # Group metrics
        self.total_groups = Gauge('openwebui_groups_total', 'Total number of groups')
        # Feedback metrics
        self.total_feedback = Gauge('openwebui_feedback_total', 'Total number of feedback entries')

        # Start collecting metrics
        self.collect_metrics()

    def collect_metrics(self):
        """Collect all system-related metrics"""
        try:
            with self.db_pool.get_connection() as cur:
                # Configuration metrics
                cur.execute("""
                    SELECT version, extract(epoch from updated_at)
                    FROM public.config
                    ORDER BY id DESC
                    LIMIT 1
                """)
                result = cur.fetchone()
                if result:
                    version, updated_at = result
                    self.config_version.set(version)
                    self.config_update_time.set(updated_at)

                # Group metrics
                cur.execute("SELECT COUNT(*) FROM public.group")
                self.total_groups.set(cur.fetchone()[0])

                # Feedback metrics
                cur.execute("SELECT COUNT(*) FROM public.feedback")
                self.total_feedback.set(cur.fetchone()[0])

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
