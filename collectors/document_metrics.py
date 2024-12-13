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
        self.documents_by_collection = Gauge('openwebui_documents_by_collection',
                                          'Number of documents by collection',
                                          ['collection_name'])
        self.documents_by_user = Gauge('openwebui_documents_by_user',
                                    'Number of documents per user',
                                    ['user_id', 'user_name', 'user_email'])

        # File metrics
        self.total_files = Gauge('openwebui_files_total', 'Total number of files',
                              ['knowledge_base_id', 'knowledge_base_name'])
        self.files_by_user = Gauge('openwebui_files_by_user',
                                'Number of files per user',
                                ['user_id', 'user_name', 'user_email'])

        # Knowledge base metrics
        self.total_knowledge_bases = Gauge('openwebui_knowledge_bases_total',
                                        'Total number of knowledge bases')
        self.knowledge_bases_by_user = Gauge('openwebui_knowledge_bases_by_user',
                                          'Number of knowledge bases per user',
                                          ['user_id', 'user_name', 'user_email', 'knowledge_name'])

        # Memory metrics
        self.total_memories = Gauge('openwebui_memories_total', 'Total number of memories')
        self.memories_by_user = Gauge('openwebui_memories_by_user',
                                   'Number of memories per user',
                                   ['user_id', 'user_name', 'user_email'])

        # Document age
        self.document_age = Histogram('openwebui_document_age_seconds',
                                   'Age of documents in seconds',
                                   buckets=[3600, 86400, 604800, 2592000, 7776000]) # 1h, 1d, 1w, 30d, 90d

        # Start collecting metrics
        self.collect_metrics()

    def collect_metrics(self):
        """Collect all document-related metrics"""
        try:
            with self.db_pool.get_connection() as cur:
                # Document metrics
                cur.execute("SELECT COUNT(*) FROM public.document")
                self.total_documents.set(cur.fetchone()[0])

                # Documents by collection
                cur.execute("""
                    SELECT collection_name, COUNT(*)
                    FROM public.document
                    GROUP BY collection_name
                """)
                for collection_name, count in cur.fetchall():
                    self.documents_by_collection.labels(
                        collection_name=collection_name
                    ).set(count)

                # Debug: Documents by user with user names and emails
                debug_query = """
                    SELECT d.user_id, u.name, u.email, COUNT(*)
                    FROM public.document d
                    JOIN public.user u ON d.user_id = u.id
                    GROUP BY d.user_id, u.name, u.email
                """
                cur.execute(debug_query)
                results = cur.fetchall()
                logger.info("Debug - Documents by user:")
                for row in results:
                    logger.info(f"User: {row[0]}, Name: {row[1]}, Email: {row[2]}, Count: {row[3]}")
                    self.documents_by_user.labels(
                        user_id=row[0],
                        user_name=row[1],
                        user_email=row[2]
                    ).set(row[3])

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

                debug_query = """
                    SELECT k.user_id, u.name, u.email, k.name, COUNT(*)
                    FROM public.knowledge k
                    JOIN public.user u ON k.user_id = u.id
                    GROUP BY k.user_id, u.name, u.email, k.name
                """
                cur.execute(debug_query)
                results = cur.fetchall()
                logger.info("Debug - Knowledge bases by user:")
                for row in results:
                    logger.info(f"User: {row[0]}, Name: {row[1]}, Email: {row[2]}, KB: {row[3]}, Count: {row[4]}")
                    self.knowledge_bases_by_user.labels(
                        user_id=row[0],
                        user_name=row[1],
                        user_email=row[2],
                        knowledge_name=row[3]
                    ).set(row[4])

                # Memory metrics with user names and emails
                cur.execute("SELECT COUNT(*) FROM public.memory")
                self.total_memories.set(cur.fetchone()[0])

                debug_query = """
                    SELECT m.user_id, u.name, u.email, COUNT(*)
                    FROM public.memory m
                    JOIN public.user u ON m.user_id = u.id
                    GROUP BY m.user_id, u.name, u.email
                """
                cur.execute(debug_query)
                results = cur.fetchall()
                logger.info("Debug - Memories by user:")
                for row in results:
                    logger.info(f"User: {row[0]}, Name: {row[1]}, Email: {row[2]}, Count: {row[3]}")
                    self.memories_by_user.labels(
                        user_id=row[0],
                        user_name=row[1],
                        user_email=row[2]
                    ).set(row[3])

                # Document age distribution
                cur.execute("SELECT timestamp FROM public.document")
                for (timestamp,) in cur.fetchall():
                    self.document_age.observe(timestamp)

        except Exception as e:
            logger.error(f"Error collecting document metrics: {e}")
