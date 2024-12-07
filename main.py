from prometheus_client import start_http_server
import time
import logging
import threading
from collectors.user_metrics import UserMetricsCollector
from collectors.chat_metrics import ChatMetricsCollector
from collectors.document_metrics import DocumentMetricsCollector
from collectors.model_metrics import ModelMetricsCollector
from collectors.system_metrics import SystemMetricsCollector
from db.connection import DatabasePool
from config import METRICS_PORT, METRICS_UPDATE_INTERVAL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetricsCollectorManager:
    def __init__(self):
        self.db_pool = DatabasePool()
        self.collectors = []
        self.initialize_collectors()

    def initialize_collectors(self):
        """Initialize all metric collectors"""
        with self.db_pool.get_connection() as db:
            self.collectors = [
                UserMetricsCollector(db),
                ChatMetricsCollector(db),
                DocumentMetricsCollector(db),
                ModelMetricsCollector(db),
                SystemMetricsCollector(db)
            ]
        logger.info("Initialized all metric collectors")

    def update_metrics(self):
        """Update all metrics"""
        try:
            with self.db_pool.get_connection() as db:
                for collector in self.collectors:
                    try:
                        collector.collect_metrics()
                    except Exception as e:
                        logger.error(f"Error updating metrics for {collector.__class__.__name__}: {e}")
        except Exception as e:
            logger.error(f"Error getting database connection: {e}")

    def start_metrics_collection(self):
        """Start periodic metrics collection"""
        while True:
            try:
                self.update_metrics()
                logger.debug(f"Updated metrics, sleeping for {METRICS_UPDATE_INTERVAL} seconds")
                time.sleep(METRICS_UPDATE_INTERVAL)
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                time.sleep(1)  # Sleep briefly before retrying

def main():
    try:
        # Start up the server to expose the metrics.
        logger.info(f"Starting OpenWebUI exporter on port {METRICS_PORT}")
        start_http_server(METRICS_PORT)
        
        # Initialize metrics collector manager
        metrics_manager = MetricsCollectorManager()
        
        # Start metrics collection in a separate thread
        collection_thread = threading.Thread(
            target=metrics_manager.start_metrics_collection,
            daemon=True
        )
        collection_thread.start()
        logger.info(f"Started metrics collection thread (interval: {METRICS_UPDATE_INTERVAL}s)")
        
        # Keep the main thread running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down OpenWebUI exporter")
        DatabasePool().close_all()
    except Exception as e:
        logger.error(f"Fatal error in main thread: {e}")
        DatabasePool().close_all()
        raise

if __name__ == '__main__':
    main()
