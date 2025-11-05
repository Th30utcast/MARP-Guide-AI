"""
INGESTION SERVICE WORKER

Entry point for the Ingestion Service. This worker:
1. Connects to RabbitMQ
2. Scrapes the MARP website for PDFs
3. Downloads each PDF
4. Publishes DocumentDiscovered events
5. Runs a health check server

Flow: Scrape → Download → Publish Events
"""

import sys
from pathlib import Path

# Setup import paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from common.config import get_rabbitmq_broker, MARP_URL, PDF_OUTPUT_DIR, STORAGE_PATH
from common.events import ROUTING_KEY_DISCOVERED, ROUTING_KEY_INGESTION_FAILED
from common.health import start_health_server
from common.logging_config import setup_logging
from ingestion_service import IngestionService

logger = setup_logging(__name__)


if __name__ == "__main__":
    logger.info("🚀 Initializing Ingestion Service Worker...")

    # Connect to RabbitMQ (Message Broker for EDA)
    try:
        broker = get_rabbitmq_broker()
        logger.info("✅ Connected to RabbitMQ")
    except Exception as e:
        logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
        logger.info("💡 Make sure RabbitMQ is running: docker-compose up -d rabbitmq")
        sys.exit(1)

    # Setup queues and exchange for event publishing
    try:
        # Create queues for DocumentDiscovered and IngestionFailed events
        broker.declare_queue(ROUTING_KEY_DISCOVERED)
        broker.declare_queue(ROUTING_KEY_INGESTION_FAILED)

        # Bind queues to exchange (topic routing)
        if broker.channel:
            broker.channel.exchange_declare(
                exchange="events",
                exchange_type="topic",
                durable=True
            )
            broker.channel.queue_bind(
                exchange="events",
                queue=ROUTING_KEY_DISCOVERED,
                routing_key=ROUTING_KEY_DISCOVERED
            )
            broker.channel.queue_bind(
                exchange="events",
                queue=ROUTING_KEY_INGESTION_FAILED,
                routing_key=ROUTING_KEY_INGESTION_FAILED
            )
        logger.info("✅ Queues and exchange configured")
    except Exception as e:
        logger.error(f"❌ Failed to configure queues: {e}")
        sys.exit(1)

    # Initialize the Ingestion Service with broker and config
    try:
        ingestion_service = IngestionService(
            event_broker=broker,
            base_url=MARP_URL,
            pdf_output_dir=PDF_OUTPUT_DIR,
            storage_path=STORAGE_PATH
        )
        logger.info("✅ Ingestion service initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize ingestion service: {e}", exc_info=True)
        sys.exit(1)

    # Start health check server on port 8000
    start_health_server(broker, service_name="ingestion-service", port=8000)

    # Run the ingestion pipeline: scrape → download → publish events
    logger.info("🚀 Starting ingestion process...")
    try:
        result = ingestion_service.run_ingestion()
        logger.info(f"📊 Ingestion result: {result}")
        logger.info("✅ Ingestion completed successfully")
    except KeyboardInterrupt:
        logger.info("\n⏹️ Shutting down gracefully...")
        ingestion_service.close()
        broker.close()
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        ingestion_service.close()
        broker.close()
        sys.exit(1)
    finally:
        ingestion_service.close()
        broker.close()
        logger.info("👋 Ingestion service shutting down")
