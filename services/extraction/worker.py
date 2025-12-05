"""
Extraction Service Worker - RabbitMQ Event Consumer Entry Point

Main entry point for the Extraction microservice. This worker process listens for
DocumentDiscovered events, processes PDFs, and publishes DocumentExtracted events.

Architecture:
    - Long-running worker process (event consumer)
    - Connects to RabbitMQ message broker for event-driven communication
    - Runs HTTP health check server in background thread for monitoring
    - Stateless: Can be scaled horizontally for parallel processing

Health Check:
    - HTTP server on port 8080 (/health endpoint)
    - Checks RabbitMQ connection status
    - Returns 200 if healthy, 503 if disconnected
    - Used by Docker health checks
"""

import json
import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
project_root = current_dir
sys.path.insert(0, str(project_root))

from extraction_service import ExtractionService

from common.config import get_rabbitmq_broker, get_storage_path
from common.events import ROUTING_KEY_DISCOVERED, ROUTING_KEY_EXTRACTED, ROUTING_KEY_EXTRACTION_FAILED
from common.health import start_health_server
from common.logging_config import setup_logging

logger = setup_logging(__name__)


def process_document_discovered(ch, method, properties, body):
    """
    - Failed extractions publish ExtractionFailed events for monitoring
    - Messages are always acknowledged (removed from queue) to prevent infinite loops
    - Processing continues with next document even if current one fails
    """
    try:
        # Decode the message body
        event = json.loads(body)

        # Validate event structure
        if "payload" not in event or "documentId" not in event.get("payload", {}):
            logger.error(f"❌ Invalid event structure: {event}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        logger.info(f"📥 Received DocumentDiscovered: {event['payload']['documentId']}")

        # Process the event
        result = extraction_service.handle_document_discovered_event(event)

        if result:
            logger.info(f"✅ Processed: {result['payload']['documentId']}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            # Extraction failed, but failure event was already published
            # Acknowledge message to remove from queue and continue processing
            logger.warning(f"⚠️ Processing failed for {event['payload']['documentId']}, but continuing...")
            ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing error: {e}")
        logger.error(f"Body content: {body}")
        # Don't requeue malformed messages - acknowledge to remove from queue
        logger.warning("⚠️ Malformed message, acknowledging to skip...")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except KeyboardInterrupt:
        # Allow graceful shutdown
        raise

    except Exception as e:
        logger.error(f"❌ Unexpected error in worker: {str(e)}", exc_info=True)
        # For unexpected worker errors, acknowledge to prevent infinite loop
        logger.warning("⚠️ Unexpected error, acknowledging to continue processing...")
        ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    logger.info("🚀 Initializing Extraction Service Worker...")

    # Initialize event broker
    try:
        broker = get_rabbitmq_broker()
        logger.info("✅ Connected to RabbitMQ")
    except Exception as e:
        logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
        logger.info("💡 Make sure RabbitMQ is running: docker-compose up -d rabbitmq")
        sys.exit(1)

    # Declare queues and exchange
    try:
        broker.declare_queue(ROUTING_KEY_DISCOVERED)
        broker.declare_queue(ROUTING_KEY_EXTRACTED)
        broker.declare_queue(ROUTING_KEY_EXTRACTION_FAILED)

        if broker.channel:
            broker.channel.exchange_declare(exchange="events", exchange_type="topic", durable=True)
            broker.channel.queue_bind(exchange="events", queue=ROUTING_KEY_DISCOVERED, routing_key=ROUTING_KEY_DISCOVERED)
            broker.channel.queue_bind(exchange="events", queue=ROUTING_KEY_EXTRACTED, routing_key=ROUTING_KEY_EXTRACTED)
            broker.channel.queue_bind(
                exchange="events", queue=ROUTING_KEY_EXTRACTION_FAILED, routing_key=ROUTING_KEY_EXTRACTION_FAILED
            )
        logger.info("✅ Queues and exchange configured")
    except Exception as e:
        logger.error(f"❌ Failed to configure queues: {e}")
        sys.exit(1)

    # Initialize extraction service with storage path
    storage_path = get_storage_path()
    extraction_service = ExtractionService(event_broker=broker, storage_path=str(storage_path))
    logger.info(f"✅ Extraction service initialized. Storage: {storage_path}")

    # Start health check server
    start_health_server(broker, service_name="extraction-service", port=8080)

    logger.info("👂 Listening for DocumentDiscovered events...")
    logger.info("Press Ctrl+C to stop")

    try:
        broker.consume(queue_name=ROUTING_KEY_DISCOVERED, callback=process_document_discovered, auto_ack=False)
    except KeyboardInterrupt:
        logger.info("\n⏹️ Shutting down gracefully...")
        broker.close()
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        broker.close()
        sys.exit(1)
