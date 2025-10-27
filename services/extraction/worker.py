"""
Extraction Service Worker
Consumes DocumentDiscovered events and publishes DocumentExtracted events.
"""

import json
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path to access common module
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from common.mq import RabbitMQEventBroker
from extraction_service import ExtractionService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_document_discovered(ch, method, properties, body):
    """Callback for processing DocumentDiscovered events."""
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
            logger.error("❌ Processing failed, requeuing...")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing error: {e}")
        logger.error(f"Body content: {body}")
        # Don't requeue malformed messages
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}", exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

if __name__ == "__main__":
    logger.info("🚀 Initializing Extraction Service Worker...")
    
    # Initialize event broker
    try:
        broker = RabbitMQEventBroker(
            host=os.getenv("RABBITMQ_HOST", "localhost"),
            port=int(os.getenv("RABBITMQ_PORT", 5672)),
            username=os.getenv("RABBITMQ_USER", "guest"),
            password=os.getenv("RABBITMQ_PASSWORD", "guest")
        )
        logger.info("✅ Connected to RabbitMQ")
    except Exception as e:
        logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
        logger.info("💡 Make sure RabbitMQ is running: docker-compose up -d rabbitmq")
        sys.exit(1)
    
    # Declare queues and exchange
    try:
        broker.declare_queue("documents.discovered")
        broker.declare_queue("documents.extracted")
        
        if broker.channel:
            broker.channel.exchange_declare(
                exchange="events",
                exchange_type="topic",
                durable=True
            )
            broker.channel.queue_bind(
                exchange="events",
                queue="documents.discovered",
                routing_key="documents.discovered"
            )
            broker.channel.queue_bind(
                exchange="events",
                queue="documents.extracted",
                routing_key="documents.extracted"
            )
        logger.info("✅ Queues and exchange configured")
    except Exception as e:
        logger.error(f"❌ Failed to configure queues: {e}")
        sys.exit(1)
    
    # Initialize extraction service with storage path
    # Storage path is relative to project root
    storage_path = project_root / "storage" / "extracted"
    extraction_service = ExtractionService(
        event_broker=broker,
        storage_path=str(storage_path)
    )
    logger.info(f"✅ Extraction service initialized. Storage: {storage_path}")
    
    logger.info("👂 Listening for DocumentDiscovered events...")
    logger.info("Press Ctrl+C to stop")
    
    try:
        broker.consume(
            queue_name="documents.discovered",
            callback=process_document_discovered,
            auto_ack=False
        )
    except KeyboardInterrupt:
        logger.info("\n⏹️ Shutting down gracefully...")
        broker.close()
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        broker.close()
        sys.exit(1)