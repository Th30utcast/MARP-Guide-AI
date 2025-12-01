"""
Indexing Service Worker - The Main Program That Runs the Indexing Service

WHAT THIS DOES:
This program waits for messages from the extraction service. When a document has been
extracted, this service chunks it, creates embeddings, and stores them in a database.

HOW IT WORKS:
1. Starts up and loads the AI model
2. Connects to RabbitMQ
3. Waits for messages saying "document extracted"
4. When a message arrives, processes that document
5. Repeats step 4 forever (until you press Ctrl+C)
"""

import json
import os
import sys
from pathlib import Path

# Add the current directory to Python's search path so we can import our code
current_dir = Path(__file__).resolve().parent
project_root = current_dir
sys.path.insert(0, str(project_root))

from indexing_service import IndexingService

from common.health import start_health_server
from common.logging_config import setup_logging
from common.mq import RabbitMQEventBroker

# Set up logging so we can see what's happening
logger = setup_logging(__name__)


# ============================================================================
# EVENT PROCESSING - This Function Runs Every Time a Message Arrives
# ============================================================================


def process_document_extracted(ch, method, properties, body):
    """
    This function is called by RabbitMQ when a new document needs indexing.

    PARAMETERS (provided by RabbitMQ):
    - ch: The channel (connection to RabbitMQ)
    - method: Message metadata (includes delivery_tag for acknowledgment)
    - properties: Message properties (not used here)
    - body: The actual message content (JSON string)

    WHAT IT DOES:
    1. Receives a message from RabbitMQ
    2. Decodes the JSON
    3. Validates it's a proper message
    4. Calls the indexing service to process the document
    5. Tells RabbitMQ "I'm done" or "skip this message"

    RESILIENCE STRATEGY:
    - Failed indexing operations publish IndexingFailed events for monitoring
    - Messages are ALWAYS acknowledged (removed from queue) to prevent infinite loops
    - Processing continues with next document even if current one fails
    - This prevents a single problematic document from blocking the entire pipeline
    """
    try:
        # Step 1: Decode the message from JSON string to Python dictionary
        event = json.loads(body)

        # Step 2: Make sure the message has the required fields
        # Every message needs a "payload" with a "documentId" inside
        if "payload" not in event or "documentId" not in event.get("payload", {}):
            logger.error(f"❌ Invalid event structure: {event}")
            # Tell RabbitMQ: "This message is broken, don't send it again"
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        # Step 3: Log that we received a message
        logger.info(f"📥 Received DocumentExtracted: {event['payload']['documentId']}")

        # Step 4: Process the document (MAIN WORK!)
        # This calls indexing_service.py which does: read → chunk → embed → store
        indexing_service.handle_document_extracted_event(event)

        # Step 5: Success! Tell RabbitMQ
        logger.info(f"✅ Indexed: {event['payload']['documentId']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e:
        # The message wasn't valid JSON (corrupted message)
        logger.error(f"❌ JSON parsing error: {e}")
        logger.error(f"Body content: {body}")
        # Don't retry broken messages
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    except Exception as e:
        # Something went wrong during indexing
        logger.error(f"❌ Error: {str(e)}", exc_info=True)
        # Acknowledge to prevent infinite loop (failure event already published by indexing_service)
        logger.warning(f"⚠️ Processing failed but continuing with next document...")
        ch.basic_ack(delivery_tag=method.delivery_tag)


# ============================================================================
# MAIN ENTRY POINT - This Runs When You Start the Program
# ============================================================================

if __name__ == "__main__":
    """
    This is where the program starts executing.

    STARTUP SEQUENCE (5 steps):
    1. Connect to RabbitMQ
    2. Set up the queues (inboxes for messages)
    3. Load the AI model and connect to the database
    4. Start the health check web server (background)
    5. Start listening for messages (runs forever)
    """
    logger.info("🚀 Initializing Indexing Service Worker...")

    # ========================================================================
    # STEP 1: CONNECT TO RABBITMQ
    # ========================================================================
    try:
        # Read connection settings from environment variables (set by Docker)
        broker = RabbitMQEventBroker(
            host=os.getenv("RABBITMQ_HOST", "localhost"),  # Where is RabbitMQ?
            port=int(os.getenv("RABBITMQ_PORT", 5672)),  # What port?
            username=os.getenv("RABBITMQ_USER", "guest"),  # Login username
            password=os.getenv("RABBITMQ_PASSWORD", "guest"),  # Login password
        )
        logger.info("✅ Connected to RabbitMQ")
    except Exception as e:
        # Connection failed
        logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
        logger.info("💡 Make sure RabbitMQ is running: docker-compose up -d rabbitmq")
        sys.exit(1)  # Exit with error code 1

    # ========================================================================
    # STEP 2: DECLARE QUEUES & EXCHANGE (Set Up Message Routing)
    # ========================================================================
    try:
        # Create the inbox queue (where extraction service sends us messages)
        broker.declare_queue("documents.extracted")

        # Create the outbox queue (where we send success notifications)
        broker.declare_queue("documents.indexed")

        # Create the failure queue (where we send failure notifications)
        broker.declare_queue("documents.indexing.failed")

        # Set up the routing system (exchange + bindings)
        if broker.channel:
            # Create a "topic" exchange
            broker.channel.exchange_declare(
                exchange="events",  # Name of the exchange
                exchange_type="topic",  # Type: topic (uses routing keys)
                durable=True,  # Survives RabbitMQ restarts
            )

            # Connect "documents.extracted" queue to the exchange
            # When someone sends a message with routing_key="documents.extracted",
            # it will arrive in our inbox
            broker.channel.queue_bind(exchange="events", queue="documents.extracted", routing_key="documents.extracted")

            # Connect "documents.indexed" queue to the exchange
            # When we send messages with routing_key="documents.indexed",
            # they'll go to this queue
            broker.channel.queue_bind(exchange="events", queue="documents.indexed", routing_key="documents.indexed")

            # Connect "documents.indexing.failed" queue to the exchange
            # When we send messages with routing_key="documents.indexing.failed",
            # they'll go to this queue for monitoring
            broker.channel.queue_bind(
                exchange="events", queue="documents.indexing.failed", routing_key="documents.indexing.failed"
            )
        logger.info("✅ Queues and exchange configured")
    except Exception as e:
        logger.error(f"❌ Failed to configure queues: {e}")
        sys.exit(1)

    # ========================================================================
    # STEP 3: INITIALIZE INDEXING SERVICE (Load AI Model & Connect to Database)
    # ========================================================================
    # We load the AI model ONCE here
    # GLOBAL VARIABLE: We create 'indexing_service' here so the callback function can use it
    try:
        # Create the IndexingService instance (loads model, connects to Qdrant)
        # This is GLOBAL - the process_document_extracted() function will use it
        indexing_service = IndexingService()
        logger.info("✅ Indexing service initialized")
    except Exception as e:
        # Loading failed
        logger.error(f"❌ Failed to initialize indexing service: {e}", exc_info=True)
        logger.info("💡 Make sure Qdrant is running: docker-compose up -d qdrant")
        sys.exit(1)

    # ========================================================================
    # STEP 4: START HEALTH CHECK SERVER (Background Thread)
    # ========================================================================
    # Start a tiny web server that Docker can check to see if we're alive.
    # This runs in the background (separate thread) so it doesn't block us.
    start_health_server(broker, service_name="indexing-service", port=8080)

    # ========================================================================
    # STEP 5: START CONSUMING EVENTS (Main Loop - Runs Forever!)
    # ========================================================================
    # Now we start listening for messages. This will BLOCK HERE and never return.
    # The program sits here waiting for messages forever (until Ctrl+C or error).
    logger.info("👂 Listening for DocumentExtracted events...")
    logger.info("Press Ctrl+C to stop")

    try:
        # Start consuming messages from the "documents.extracted" queue
        # Every time a message arrives, RabbitMQ will call process_document_extracted()
        broker.consume(
            queue_name="documents.extracted",  # Which queue to listen to
            callback=process_document_extracted,  # What function to call for each message
            auto_ack=False,  # We'll manually acknowledge
        )

    except KeyboardInterrupt:
        # User pressed Ctrl+C - shut down gracefully
        logger.info("\n⏹️ Shutting down gracefully...")
        indexing_service.close()  # Close database connections
        broker.close()  # Close RabbitMQ connection
        logger.info("👋 Goodbye!")

    except Exception as e:
        # crash and log the error
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        indexing_service.close()
        broker.close()
        sys.exit(1)  # Exit with error code
