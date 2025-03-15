from prometheus_client import Gauge, Counter
import logging
import json

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
        self.users_in_groups = Gauge('openwebui_users_in_groups',
                                  'Number of users in groups',
                                  ['group_id', 'group_name', 'owner_id', 'owner_name', 'owner_email'])

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

                # Debug: Group metrics with names and emails
                cur.execute("SELECT COUNT(*) FROM public.group")
                self.total_groups.set(cur.fetchone()[0])

                debug_query = """
                    SELECT
                        g.id as group_id,
                        g.name as group_name,
                        g.user_id as owner_id,
                        u.name as owner_name,
                        u.email as owner_email,
                        g.user_ids
                    FROM public.group g
                    JOIN public.user u ON g.user_id = u.id
                    WHERE g.user_ids IS NOT NULL
                """
                cur.execute(debug_query)
                results = cur.fetchall()
                logger.info("Debug - Groups and owners:")
                for row in results:
                    group_id, group_name, owner_id, owner_name, owner_email, user_ids = row
                    logger.info(f"Group: {group_id}, Name: {group_name}, Owner: {owner_id}, Owner Name: {owner_name}, Owner Email: {owner_email}, Users: {len(user_ids) if user_ids else 0}")
                    if user_ids:
                        try:
                            users = user_ids
                            self.users_in_groups.labels(
                                group_id=group_id,
                                group_name=group_name or 'unnamed',
                                owner_id=owner_id,
                                owner_name=owner_name,
                                owner_email=owner_email
                            ).set(len(users))
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse user_ids JSON for group {group_id}")

                # Debug: Feedback metrics with user names and emails
                cur.execute("SELECT COUNT(*) FROM public.feedback")
                self.total_feedback.set(cur.fetchone()[0])

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
