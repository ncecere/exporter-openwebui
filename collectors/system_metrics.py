from prometheus_client import Gauge, Counter
import logging
import json

logger = logging.getLogger(__name__)

class SystemMetricsCollector:
    """Collector for system-level metrics"""

    def __init__(self, db):
        self.db = db

        # Configuration metrics
        self.config_version = Gauge('openwebui_config_version', 'Current configuration version')
        self.config_update_time = Gauge('openwebui_config_last_update',
                                     'Timestamp of last configuration update')

        # Group metrics
        self.total_groups = Gauge('openwebui_groups_total', 'Total number of groups')
        self.users_in_groups = Gauge('openwebui_users_in_groups',
                                  'Number of users in groups',
                                  ['group_id', 'group_name', 'owner_id', 'owner_name'])

        # Feedback metrics
        self.total_feedback = Gauge('openwebui_feedback_total', 'Total number of feedback entries')
        self.feedback_by_type = Gauge('openwebui_feedback_by_type',
                                   'Number of feedback entries by type',
                                   ['type', 'user_id', 'user_name'])

        # Start collecting metrics
        self.collect_metrics()

    def collect_metrics(self):
        """Collect all system-related metrics"""
        try:
            with self.db.cursor() as cur:
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

                # Group metrics with names
                cur.execute("SELECT COUNT(*) FROM public.group")
                self.total_groups.set(cur.fetchone()[0])

                cur.execute("""
                    SELECT
                        g.id as group_id,
                        g.name as group_name,
                        g.user_id as owner_id,
                        u.name as owner_name,
                        g.user_ids
                    FROM public.group g
                    JOIN public.user u ON g.user_id = u.id
                    WHERE g.user_ids IS NOT NULL
                """)
                for group_id, group_name, owner_id, owner_name, user_ids in cur.fetchall():
                    if user_ids:
                        try:
                            users = user_ids
                            self.users_in_groups.labels(
                                group_id=group_id,
                                group_name=group_name or 'unnamed',
                                owner_id=owner_id,
                                owner_name=owner_name
                            ).set(len(users))
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse user_ids JSON for group {group_id}")

                # Feedback metrics with user names
                cur.execute("SELECT COUNT(*) FROM public.feedback")
                self.total_feedback.set(cur.fetchone()[0])

                cur.execute("""
                    SELECT
                        f.type,
                        f.user_id,
                        u.name as user_name,
                        COUNT(*)
                    FROM public.feedback f
                    LEFT JOIN public.user u ON f.user_id = u.id
                    WHERE f.type IS NOT NULL
                    GROUP BY f.type, f.user_id, u.name
                """)
                for feedback_type, user_id, user_name, count in cur.fetchall():
                    self.feedback_by_type.labels(
                        type=feedback_type,
                        user_id=user_id or 'anonymous',
                        user_name=user_name or 'anonymous'
                    ).set(count)

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
