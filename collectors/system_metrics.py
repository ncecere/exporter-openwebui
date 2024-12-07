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

        # Migration metrics
        self.total_migrations = Gauge('openwebui_migrations_total',
                                   'Total number of database migrations')
        self.last_migration_time = Gauge('openwebui_last_migration_timestamp',
                                      'Timestamp of last database migration')

        # Database table metrics
        self.table_sizes = Gauge('openwebui_table_size_bytes',
                               'Size of database tables in bytes',
                               ['table_name'])
        self.table_rows = Gauge('openwebui_table_rows',
                              'Number of rows in database tables',
                              ['table_name'])

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

                # Migration metrics
                cur.execute("SELECT COUNT(*) FROM public.migratehistory")
                self.total_migrations.set(cur.fetchone()[0])

                cur.execute("""
                    SELECT extract(epoch from migrated_at)
                    FROM public.migratehistory
                    ORDER BY id DESC
                    LIMIT 1
                """)
                result = cur.fetchone()
                if result:
                    self.last_migration_time.set(result[0])

                # Table statistics
                # Get table sizes
                cur.execute("""
                    SELECT
                        schemaname || '.' || tablename as table_name,
                        pg_total_relation_size(schemaname || '.' || tablename) as total_bytes
                    FROM pg_catalog.pg_tables
                    WHERE schemaname = 'public'
                """)
                for table_name, total_bytes in cur.fetchall():
                    self.table_sizes.labels(table_name=table_name).set(total_bytes)

                # Get row counts for each table
                tables_query = """
                    SELECT schemaname || '.' || tablename as table_name
                    FROM pg_catalog.pg_tables
                    WHERE schemaname = 'public'
                """
                cur.execute(tables_query)
                for (table_name,) in cur.fetchall():
                    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cur.fetchone()[0]
                    self.table_rows.labels(table_name=table_name).set(row_count)

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
                            users = json.loads(user_ids)
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
