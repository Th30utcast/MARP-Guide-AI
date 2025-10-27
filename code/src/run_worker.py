"""
Run the extraction worker to process DocumentDiscovered events from the queue.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import from extraction
from extraction.event_broker import RabbitMQEventBroker
from extraction.extraction_service import ExtractionService
import json
import logging
import os as os_module

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_document_discovered(ch, method, properties, body):
    """
    Callback function for processing DocumentDiscovered events.
    
    Args:
        ch: Channel
        method: Delivery method
        properties: Message properties
        body: Message body
    """
    try:
        event = json.loads(body)
        logger.info(f"Received DocumentDiscovered event: {event['payload']['documentId']}")
        
        # Process the event
        result = extraction_service.handle_document_discovered_event(event)
        
        if result:
            logger.info(f"Successfully processed document: {result['payload']['documentId']}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            logger.error("Failed to process document, requeuing...")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


if __name__ == "__main__":
    # Initialize event broker
    broker = RabbitMQEventBroker(
        host=os_module.getenv("RABBITMQ_HOST", "localhost"),
        port=int(os_module.getenv("RABBITMQ_PORT", 5672)),
        username=os_module.getenv("RABBITMQ_USER", "guest"),
        password=os_module.getenv("RABBITMQ_PASSWORD", "guest")
    )
    
    # Declare the necessary queues
    broker.declare_queue("documents.discovered")
    broker.declare_queue("documents.extracted")
    
    # Bind queue to exchange (if using fanout or topic exchange)
    if broker.channel:
        broker.channel.exchange_declare(exchange="events", exchange_type="topic", durable=True)
        broker.channel.queue_bind(
            exchange="events",
            queue="documents.discovered",
            routing_key="documents.discovered"
        )
    
    # Initialize extraction service
    extraction_service = ExtractionService(event_broker=broker)
    
    logger.info("Starting Extraction Service worker...")
    
    try:
        # Start consuming from DocumentDiscovered queue
        broker.consume(
            queue_name="documents.discovered",
            callback=process_document_discovered,
            auto_ack=False
        )
    except KeyboardInterrupt:
        logger.info("Shutting down Extraction Service...")
        broker.close()