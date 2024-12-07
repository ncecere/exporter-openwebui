from prometheus_client import Gauge, Counter, Histogram
import logging

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
                                    ['user_id'])
        
        # File metrics
        self.total_files = Gauge('openwebui_files_total', 'Total number of files')
        self.files_by_user = Gauge('openwebui_files_by_user',
                                'Number of files per user',
                                ['user_id'])
        
        # Knowledge base metrics
        self.total_knowledge_bases = Gauge('openwebui_knowledge_bases_total',
                                        'Total number of knowledge bases')
        self.knowledge_bases_by_user = Gauge('openwebui_knowledge_bases_by_user',
                                          'Number of knowledge bases per user',
                                          ['user_id'])
        
        # Memory metrics
        self.total_memories = Gauge('openwebui_memories_total', 'Total number of memories')
        self.memories_by_user = Gauge('openwebui_memories_by_user',
                                   'Number of memories per user',
                                   ['user_id'])
        
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
                        collection_name=collection_name).set(count)
                
                # Documents by user
                cur.execute("""
                    SELECT user_id, COUNT(*) 
                    FROM public.document 
                    GROUP BY user_id
                """)
                for user_id, count in cur.fetchall():
                    self.documents_by_user.labels(user_id=user_id).set(count)
                
                # File metrics
                cur.execute("SELECT COUNT(*) FROM public.file")
                self.total_files.set(cur.fetchone()[0])
                
                cur.execute("""
                    SELECT user_id, COUNT(*) 
                    FROM public.file 
                    GROUP BY user_id
                """)
                for user_id, count in cur.fetchall():
                    self.files_by_user.labels(user_id=user_id).set(count)
                
                # Knowledge base metrics
                cur.execute("SELECT COUNT(*) FROM public.knowledge")
                self.total_knowledge_bases.set(cur.fetchone()[0])
                
                cur.execute("""
                    SELECT user_id, COUNT(*) 
                    FROM public.knowledge 
                    GROUP BY user_id
                """)
                for user_id, count in cur.fetchall():
                    self.knowledge_bases_by_user.labels(user_id=user_id).set(count)
                
                # Memory metrics
                cur.execute("SELECT COUNT(*) FROM public.memory")
                self.total_memories.set(cur.fetchone()[0])
                
                cur.execute("""
                    SELECT user_id, COUNT(*) 
                    FROM public.memory 
                    GROUP BY user_id
                """)
                for user_id, count in cur.fetchall():
                    self.memories_by_user.labels(user_id=user_id).set(count)
                
                # Document age distribution
                cur.execute("SELECT timestamp FROM public.document")
                for (timestamp,) in cur.fetchall():
                    self.document_age.observe(timestamp)
                
        except Exception as e:
            logger.error(f"Error collecting document metrics: {e}")
