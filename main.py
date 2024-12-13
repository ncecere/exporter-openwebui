from prometheus_client import start_http_server
import time
import logging
import threading
from collectors.user_metrics import UserMetricsCollector
from collectors.chat_metrics import ChatMetricsCollector
from collectors.document_metrics import DocumentMetricsCollector
from collectors.model_metrics import ModelMetricsCollector
from collectors.system_metrics import SystemMetricsCollector
from db.connection import get_db_pool
from config import METRICS_PORT, METRICS_UPDATE_INTERVAL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetricsCollectorManager:
    def __init__(self):
        self.db_pool = get_db_pool()
        self.collectors = []
        self.initialize_collectors()

    def initialize_collectors(self):
        """Initialize all metric collectors"""
        self.collectors = [
            UserMetricsCollector(self.db_pool),
            ChatMetricsCollector(self.db_pool),
            DocumentMetricsCollector(self.db_pool),
            ModelMetricsCollector(self.db_pool),
            SystemMetricsCollector(self.db_pool)
        ]
        logger.info("Initialized all metric collectors")

    def update_metrics(self):
        """Update all metrics"""
        for collector in self.collectors:
            try:
                collector.collect_metrics()
            except Exception as e:
                logger.error(f"Error updating metrics for {collector.__class__.__name__}: {e}")

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
        get_db_pool().close_all()
    except Exception as e:
        logger.error(f"Fatal error in main thread: {e}")
        get_db_pool().close_all()
        raise

if __name__ == '__main__':
    main()
