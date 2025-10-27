"""
Local test script for DocumentExtracted event using your actual code.
This simulates DocumentDiscovered events from test-pdfs/ and tests extraction.
"""
"""
Local test script for Extraction Service
"""

import json
import time
import threading
import logging
import sys
import os
from pathlib import Path
from datetime import datetime, timezone
import uuid

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'C:\\Users\\user\\Desktop\\VS Code\\Uni\\Year 3\\MARP-Guide-AI\\common'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'C:\\Users\\user\\Desktop\\VS Code\\Uni\\Year 3\\MARP-Guide-AI\\services\\extraction'))

from common.mq import RabbitMQEventBroker  # use explicit package path so static analyzers can resolve it
from services.extraction.extraction_service import ExtractionService  # use explicit package path so static analyzers can resolve it

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TEST_PDFS_DIR = "test-pdfs"

# ... rest of your code stays the same
#!! Delete this once tino makes the DocumentDiscovered event
def create_document_discovered_event(file_path: str, title: str) -> dict:
    """Create a DocumentDiscovered event from a test PDF."""
    return {
        "eventType": "DocumentDiscovered",
        "eventId": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "correlationId": str(uuid.uuid4()),
        "source": "test-script",
        "version": "1.0",
        "payload": {
            "documentId": f"test-{Path(file_path).stem}",
            "title": title,
            "url": str(Path(file_path).absolute()),
            "discoveredAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "fileSize": Path(file_path).stat().st_size
        }
    }


def consume_extracted_events(broker, extraction_service):
    """Consume and print DocumentExtracted events."""
    
    def callback(ch, method, properties, body):
        try:
            event = json.loads(body)
            logger.info("=" * 80)
            logger.info("✅ RECEIVED DOCUMENTEXTRACTED EVENT:")
            logger.info("=" * 80)
            logger.info(json.dumps(event, indent=2))
            logger.info("=" * 80)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing extracted event: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    logger.info("🔍 Listening for DocumentExtracted events...")
    broker.consume(
        queue_name="documents.extracted",
        callback=callback,
        auto_ack=False
    )


def main():
    logger.info("🚀 Starting local extraction test...")
    
    # Initialize broker
    try:
        broker = RabbitMQEventBroker(
            host="localhost",
            port=5672,
            username="guest",
            password="guest"
        )
        logger.info("✅ Connected to RabbitMQ")
    except Exception as e:
        logger.error(f"❌ Failed to connect to RabbitMQ: {str(e)}")
        logger.info("💡 Make sure RabbitMQ is running: docker-compose up -d")
        return
    
    # Declare queues
    broker.declare_queue("documents.discovered")
    broker.declare_queue("documents.extracted")
    
    # Declare exchange
    if broker.channel:
        broker.channel.exchange_declare(exchange="events", exchange_type="topic", durable=True)
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
    
    # Initialize extraction service
    extraction_service = ExtractionService(event_broker=broker)
    logger.info("✅ Extraction service initialized")
    
    # Start consumer thread for extracted events
    consumer_thread = threading.Thread(
        target=consume_extracted_events,
        args=(broker, extraction_service),
        daemon=True
    )
    consumer_thread.start()
    
    # Give consumer time to start
    time.sleep(1)
    
    # Find and process test PDFs
    pdf_files = list(Path(TEST_PDFS_DIR).glob("*.pdf"))
    
    if not pdf_files:
        logger.error(f"❌ No PDFs found in {TEST_PDFS_DIR}")
        broker.close()
        return
    
    logger.info(f"📄 Found {len(pdf_files)} PDF(s) to test:\n")
    
    for pdf_path in pdf_files:
        try:
            logger.info(f"Processing: {pdf_path.name}")
            
            # Create simulated DocumentDiscovered event
            discovered_event = create_document_discovered_event(
                str(pdf_path),
                pdf_path.stem
            )
            
            logger.info(f"📤 Publishing DocumentDiscovered event for: {pdf_path.name}")
            
            # Publish to queue
            broker.publish(
                routing_key="documents.discovered",
                message=json.dumps(discovered_event),
                exchange="events"
            )
            
            # Wait a moment for processing
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {str(e)}")
    
    logger.info("\n✅ All PDFs published. Listening for results (Ctrl+C to exit)...")
    
    try:
        # Keep the consumer thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n⏹️ Stopping test...")
        broker.close()


if __name__ == "__main__":
    main()