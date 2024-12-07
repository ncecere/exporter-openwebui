from prometheus_client import Gauge, Counter, Histogram
import logging
import json

logger = logging.getLogger(__name__)

class DocumentMetricsCollector:
    """Collector for document and file-related metrics"""

    def __init__(self, db):
        self.db = db

        # Document metrics
        self.total_documents = Gauge('openwebui_documents_total', 'Total number of documents')
        self.documents_by_collection = Gauge('openwebui_documents_by_collection',
                                          'Number of documents by collection',
                                          ['collection_name'])
        self.documents_by_user = Gauge('openwebui_documents_by_user',
                                    'Number of documents per user',
                                    ['user_id', 'user_name'])

        # File metrics
        self.total_files = Gauge('openwebui_files_total', 'Total number of files',
                              ['knowledge_base_id', 'knowledge_base_name'])
        self.files_by_user = Gauge('openwebui_files_by_user',
                                'Number of files per user',
                                ['user_id', 'user_name'])

        # Knowledge base metrics
        self.total_knowledge_bases = Gauge('openwebui_knowledge_bases_total',
                                        'Total number of knowledge bases')
        self.knowledge_bases_by_user = Gauge('openwebui_knowledge_bases_by_user',
                                          'Number of knowledge bases per user',
                                          ['user_id', 'user_name', 'knowledge_name'])

        # Memory metrics
        self.total_memories = Gauge('openwebui_memories_total', 'Total number of memories')
        self.memories_by_user = Gauge('openwebui_memories_by_user',
                                   'Number of memories per user',
                                   ['user_id', 'user_name'])

        # Document age
        self.document_age = Histogram('openwebui_document_age_seconds',
                                   'Age of documents in seconds',
                                   buckets=[3600, 86400, 604800, 2592000, 7776000]) # 1h, 1d, 1w, 30d, 90d

        # Start collecting metrics
        self.collect_metrics()

    def collect_metrics(self):
        """Collect all document-related metrics"""
        try:
            with self.db.cursor() as cur:
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

                # Documents by user with user names
                cur.execute("""
                    SELECT d.user_id, u.name, COUNT(*)
                    FROM public.document d
                    JOIN public.user u ON d.user_id = u.id
                    GROUP BY d.user_id, u.name
                """)
                for user_id, user_name, count in cur.fetchall():
                    self.documents_by_user.labels(
                        user_id=user_id,
                        user_name=user_name
                    ).set(count)

                # First, set total files count (system-wide)
                cur.execute("SELECT COUNT(*) FROM public.file")
                total_count = cur.fetchone()[0]
                self.total_files.labels(
                    knowledge_base_id='none',
                    knowledge_base_name='system'
                ).set(total_count)

                # Then set files per knowledge base
                cur.execute("""
                    SELECT
                        k.id as kb_id,
                        k.name as kb_name,
                        COUNT(f.id) as file_count
                    FROM public.knowledge k
                    LEFT JOIN public.file f ON f.meta->>'collection_name' = k.id
                    GROUP BY k.id, k.name
                """)
                for kb_id, kb_name, count in cur.fetchall():
                    if kb_id:  # Only set if we have a valid knowledge base
                        self.total_files.labels(
                            knowledge_base_id=kb_id,
                            knowledge_base_name=kb_name
                        ).set(count)

                # Files by user with user names
                cur.execute("""
                    SELECT f.user_id, u.name, COUNT(*)
                    FROM public.file f
                    JOIN public.user u ON f.user_id = u.id
                    GROUP BY f.user_id, u.name
                """)
                for user_id, user_name, count in cur.fetchall():
                    self.files_by_user.labels(
                        user_id=user_id,
                        user_name=user_name
                    ).set(count)

                # Knowledge base metrics with names
                cur.execute("SELECT COUNT(*) FROM public.knowledge")
                self.total_knowledge_bases.set(cur.fetchone()[0])

                cur.execute("""
                    SELECT k.user_id, u.name, k.name, COUNT(*)
                    FROM public.knowledge k
                    JOIN public.user u ON k.user_id = u.id
                    GROUP BY k.user_id, u.name, k.name
                """)
                for user_id, user_name, knowledge_name, count in cur.fetchall():
                    self.knowledge_bases_by_user.labels(
                        user_id=user_id,
                        user_name=user_name,
                        knowledge_name=knowledge_name
                    ).set(count)

                # Memory metrics with user names
                cur.execute("SELECT COUNT(*) FROM public.memory")
                self.total_memories.set(cur.fetchone()[0])

                cur.execute("""
                    SELECT m.user_id, u.name, COUNT(*)
                    FROM public.memory m
                    JOIN public.user u ON m.user_id = u.id
                    GROUP BY m.user_id, u.name
                """)
                for user_id, user_name, count in cur.fetchall():
                    self.memories_by_user.labels(
                        user_id=user_id,
                        user_name=user_name
                    ).set(count)

                # Document age distribution
                cur.execute("SELECT timestamp FROM public.document")
                for (timestamp,) in cur.fetchall():
                    self.document_age.observe(timestamp)

        except Exception as e:
            logger.error(f"Error collecting document metrics: {e}")
