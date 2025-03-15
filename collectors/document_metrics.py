from prometheus_client import Gauge, Counter, Histogram
import logging
import json

logger = logging.getLogger(__name__)

class DocumentMetricsCollector:
    """Collector for document and file-related metrics"""

    def __init__(self, db_pool):
        self.db_pool = db_pool

        # Document metrics
        self.total_documents = Gauge('openwebui_documents_total', 'Total number of documents')

        # File metrics
        self.total_files = Gauge('openwebui_files_total', 'Total number of files')
        self.files_by_user = Gauge('openwebui_files_by_user',
                                'Number of files per user',
                                ['user_id', 'user_name', 'user_email'])

        # Knowledge base metrics
        self.total_knowledge_bases = Gauge('openwebui_knowledge_bases_total',
                                        'Total number of knowledge bases')

        # Prompt metrics
        self.total_prompts = Gauge('openwebui_prompts_total', 'Total number of prompts')

        # Start collecting metrics
        self.collect_metrics()

    def collect_metrics(self):
        """Collect all document-related metrics"""
        try:
            with self.db_pool.get_connection() as cur:
                # Document metrics
                cur.execute("SELECT COUNT(*) FROM public.document")
                self.total_documents.set(cur.fetchone()[0])

                # Total files
                cur.execute("SELECT COUNT(*) FROM public.file")
                self.total_files.set(cur.fetchone()[0])

                # Files by user with user names and emails
                debug_query = """
                    SELECT f.user_id, u.name, u.email, COUNT(*)
                    FROM public.file f
                    JOIN public.user u ON f.user_id = u.id
                    GROUP BY f.user_id, u.name, u.email
                """
                cur.execute(debug_query)
                results = cur.fetchall()
                logger.info("Debug - Files by user:")
                for row in results:
                    logger.info(f"User: {row[0]}, Name: {row[1]}, Email: {row[2]}, Count: {row[3]}")
                    self.files_by_user.labels(
                        user_id=row[0],
                        user_name=row[1],
                        user_email=row[2]
                    ).set(row[3])

                # Knowledge base metrics with names and emails
                cur.execute("SELECT COUNT(*) FROM public.knowledge")
                self.total_knowledge_bases.set(cur.fetchone()[0])

                # Total prompts
                cur.execute("SELECT COUNT(*) FROM public.prompt")
                self.total_prompts.set(cur.fetchone()[0])

        except Exception as e:
            logger.error(f"Error collecting document metrics: {e}")
