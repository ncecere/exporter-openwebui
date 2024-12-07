from prometheus_client import Gauge, Counter, Histogram
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatMetricsCollector:
    """Collector for chat-related metrics"""
    
    def __init__(self, db):
        self.db = db
        
        # Chat counts
        self.total_chats = Gauge('openwebui_chats_total', 'Total number of chats')
        self.active_chats = Gauge('openwebui_chats_active', 'Number of non-archived chats')
        self.archived_chats = Gauge('openwebui_chats_archived', 'Number of archived chats')
        self.pinned_chats = Gauge('openwebui_chats_pinned', 'Number of pinned chats')
        
        # Chat metrics by user
        self.chats_by_user = Gauge('openwebui_chats_by_user', 
                                 'Number of chats per user', ['user_id'])
        
        # Shared chats
        self.shared_chats = Gauge('openwebui_chats_shared', 'Number of shared chats')
        
        # Chat activity
        self.chat_messages = Gauge('openwebui_chat_messages_total', 
                                'Total number of chat messages')
        self.chat_age = Histogram('openwebui_chat_age_seconds',
                               'Age of chats in seconds',
                               buckets=[3600, 86400, 604800, 2592000, 7776000]) # 1h, 1d, 1w, 30d, 90d
        
        # Folder metrics
        self.folders_total = Gauge('openwebui_folders_total', 'Total number of chat folders')
        self.chats_in_folders = Gauge('openwebui_chats_in_folders', 
                                   'Number of chats organized in folders')
        
        # Start collecting metrics
        self.collect_metrics()
    
    def collect_metrics(self):
        """Collect all chat-related metrics"""
        try:
            with self.db.cursor() as cur:
                # Total chats
                cur.execute("SELECT COUNT(*) FROM public.chat")
                self.total_chats.set(cur.fetchone()[0])
                
                # Active vs archived chats
                cur.execute("SELECT COUNT(*) FROM public.chat WHERE archived = false")
                self.active_chats.set(cur.fetchone()[0])
                
                cur.execute("SELECT COUNT(*) FROM public.chat WHERE archived = true")
                self.archived_chats.set(cur.fetchone()[0])
                
                # Pinned chats
                cur.execute("SELECT COUNT(*) FROM public.chat WHERE pinned = true")
                self.pinned_chats.set(cur.fetchone()[0])
                
                # Chats by user
                cur.execute("""
                    SELECT user_id, COUNT(*) 
                    FROM public.chat 
                    GROUP BY user_id
                """)
                for user_id, count in cur.fetchall():
                    self.chats_by_user.labels(user_id=user_id).set(count)
                
                # Shared chats
                cur.execute("SELECT COUNT(*) FROM public.chat WHERE share_id IS NOT NULL")
                self.shared_chats.set(cur.fetchone()[0])
                
                # Chat age distribution
                current_time = int(datetime.now().timestamp())
                cur.execute("SELECT created_at FROM public.chat")
                for (created_at,) in cur.fetchall():
                    age = current_time - created_at
                    self.chat_age.observe(age)
                
                # Folder metrics
                cur.execute("SELECT COUNT(*) FROM public.folder")
                self.folders_total.set(cur.fetchone()[0])
                
                cur.execute("SELECT COUNT(*) FROM public.chat WHERE folder_id IS NOT NULL")
                self.chats_in_folders.set(cur.fetchone()[0])
                
                # Message count estimation (from chat JSON)
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM public.chat 
                    WHERE chat IS NOT NULL
                """)
                self.chat_messages.set(cur.fetchone()[0])
                
        except Exception as e:
            logger.error(f"Error collecting chat metrics: {e}")
