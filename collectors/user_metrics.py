from prometheus_client import Gauge, Counter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserMetricsCollector:
    """Collector for user-related metrics"""

    def __init__(self, db):
        self.db = db

        # User counts
        self.total_users = Gauge('openwebui_users_total', 'Total number of registered users')
        self.active_users = Gauge('openwebui_users_active', 'Number of active users')
        self.users_by_role = Gauge('openwebui_users_by_role', 'Number of users by role', ['role'])

        # Authentication metrics
        self.auth_active = Gauge('openwebui_auth_active', 'Number of active auth entries')
        self.oauth_users = Gauge('openwebui_oauth_users', 'Number of users using OAuth')

        # User activity
        self.user_last_active = Gauge('openwebui_user_last_active_seconds',
                                    'Timestamp of last user activity',
                                    ['user_id', 'user_name'])

        # Start collecting metrics
        self.collect_metrics()

    def collect_metrics(self):
        """Collect all user-related metrics"""
        try:
            with self.db.cursor() as cur:
                # Total users
                cur.execute("SELECT COUNT(*) FROM public.user")
                self.total_users.set(cur.fetchone()[0])

                # Active users (active in last 24 hours)
                cur.execute("""
                    SELECT COUNT(*) FROM public.user
                    WHERE last_active_at >= extract(epoch from now() - interval '24 hours')
                """)
                self.active_users.set(cur.fetchone()[0])

                # Users by role
                cur.execute("""
                    SELECT role, COUNT(*) FROM public.user
                    GROUP BY role
                """)
                for role, count in cur.fetchall():
                    self.users_by_role.labels(role=role).set(count)

                # Active auth entries
                cur.execute("SELECT COUNT(*) FROM public.auth WHERE active = true")
                self.auth_active.set(cur.fetchone()[0])

                # OAuth users
                cur.execute("SELECT COUNT(*) FROM public.user WHERE oauth_sub IS NOT NULL")
                self.oauth_users.set(cur.fetchone()[0])

                # Last active timestamps with user names
                cur.execute("SELECT id, name, last_active_at FROM public.user")
                for user_id, user_name, last_active in cur.fetchall():
                    self.user_last_active.labels(
                        user_id=user_id,
                        user_name=user_name
                    ).set(last_active)

        except Exception as e:
            logger.error(f"Error collecting user metrics: {e}")
