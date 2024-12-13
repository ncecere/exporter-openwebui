from prometheus_client import Gauge, Counter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserMetricsCollector:
    """Collector for user-related metrics"""

    def __init__(self, db_pool):
        self.db_pool = db_pool

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
                                    ['user_id', 'user_name', 'user_email'])

        # Start collecting metrics
        self.collect_metrics()

    def collect_metrics(self):
        """Collect all user-related metrics"""
        try:
            with self.db_pool.get_connection() as cur:
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

                # Debug: Last active timestamps with user names and emails
                debug_query = """
                    SELECT id, name, email, last_active_at
                    FROM public.user
                """
                cur.execute(debug_query)
                results = cur.fetchall()
                logger.info("Debug - User activity:")
                for row in results:
                    user_id, user_name, user_email, last_active = row
                    logger.info(f"User: {user_id}, Name: {user_name}, Email: {user_email}, Last Active: {last_active}")
                    self.user_last_active.labels(
                        user_id=user_id,
                        user_name=user_name,
                        user_email=user_email
                    ).set(last_active)

        except Exception as e:
            logger.error(f"Error collecting user metrics: {e}")
