"""
Indexing Service Worker - The Main Program That Runs the Indexing Service

WHAT THIS DOES:
This program waits for messages from the extraction service. When a document has been
extracted, this service chunks it, creates embeddings, and stores them in a database.

HOW IT WORKS:
1. Starts up and loads the AI model (takes about 30 seconds)
2. Connects to RabbitMQ (the message system)
3. Waits for messages saying "document extracted"
4. When a message arrives, processes that document
5. Repeats step 4 forever (until you press Ctrl+C)
"""

import json
import logging
import os
import sys
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler


# Add the current directory to Python's search path so we can import our code
current_dir = Path(__file__).resolve().parent
project_root = current_dir
sys.path.insert(0, str(project_root))

from common.mq import RabbitMQEventBroker
from indexing_service import IndexingService

# Set up logging so we can see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# HEALTH CHECK - Runs in Background to Tell Docker "I'm Still Alive"
# ============================================================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    """
    Simple web server that responds to health checks.

    Docker will visit http://localhost:8080/health every 30 seconds to check
    if this service is still working. We respond with "healthy" or "unhealthy".
    """

    broker = None  # This will be set later to our RabbitMQ connection

    def do_GET(self):
        """Handle web requests (when someone visits /health)."""
        if self.path == '/health':
            # Check if we're still connected to RabbitMQ
            is_healthy = (
                self.broker is not None and
                self.broker.connection is not None and
                not self.broker.connection.is_closed and
                self.broker.channel is not None and
                self.broker.channel.is_open
            )

            if is_healthy:
                # Everything is working! Send back HTTP 200 (success)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "healthy",
                    "service": "indexing-service",
                    "rabbitmq": "connected"
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                # Something is wrong! Send back HTTP 503 (service unavailable)
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "unhealthy",
                    "service": "indexing-service",
                    "rabbitmq": "disconnected"
                }
                self.wfile.write(json.dumps(response).encode())
        else:
            # Someone visited a page that doesn't exist
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Turn off the health check's logging (it's too noisy)."""
        pass


def start_health_server(broker, port=8080):
    """
    Start a tiny web server in the background for health checks.

    This runs on a separate thread so it doesn't block the main program.
    Docker will check http://localhost:8080/health to see if we're alive.
    """
    # Give the health checker access to our RabbitMQ connection
    HealthCheckHandler.broker = broker

    def run_server():
        """This function runs in a background thread."""
        try:
            # Create a web server listening on all network interfaces, port 8080
            server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
            logger.info(f"✅ Health check server started on port {port}")
            # serve_forever() runs until the program exits
            server.serve_forever()
        except Exception as e:
            logger.error(f"❌ Failed to start health server: {e}")

    # Start the web server in a background thread (daemon=True means it dies when main program exits)
    health_thread = threading.Thread(target=run_server, daemon=True)
    health_thread.start()


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
    5. Tells RabbitMQ "I'm done" or "retry this message"

    IMPORTANT: This uses the 'indexing_service' variable that was created
    at the bottom of this file in the main section. That way we only load
    the AI model once, not for every message!
    """
    # Tell Python we're using the global variable (created in main below)
    global indexing_service

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

        # Step 5: Success! Tell RabbitMQ "I finished processing this message"
        logger.info(f"✅ Indexed: {event['payload']['documentId']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e:
        # The message wasn't valid JSON (corrupted message)
        logger.error(f"❌ JSON parsing error: {e}")
        logger.error(f"Body content: {body}")
        # Don't retry broken messages
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    except Exception as e:
        # Something went wrong
        logger.error(f"❌ Error: {str(e)}", exc_info=True)
        # Tell RabbitMQ: "Put this message back in the queue, I'll try again later"
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


# ============================================================================
# MAIN ENTRY POINT - This Runs When You Start the Program
# ============================================================================

if __name__ == "__main__":
    """
    This is where the program starts executing.

    STARTUP SEQUENCE (5 steps):
    1. Connect to RabbitMQ (the messaging system)
    2. Set up the queues (inboxes for messages)
    3. Load the AI model and connect to the database (takes ~30 seconds)
    4. Start the health check web server (background)
    5. Start listening for messages (runs forever)
    """
    logger.info("🚀 Initializing Indexing Service Worker...")

    # ========================================================================
    # STEP 1: CONNECT TO RABBITMQ (The Message Broker)
    # ========================================================================
    try:
        # Read connection settings from environment variables (set by Docker)
        broker = RabbitMQEventBroker(
            host=os.getenv("RABBITMQ_HOST", "localhost"),      # Where is RabbitMQ?
            port=int(os.getenv("RABBITMQ_PORT", 5672)),        # What port?
            username=os.getenv("RABBITMQ_USER", "guest"),      # Login username
            password=os.getenv("RABBITMQ_PASSWORD", "guest")   # Login password
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

        # Set up the routing system (exchange + bindings)
        if broker.channel:
            # Create a "topic" exchange (a smart router for messages)
            broker.channel.exchange_declare(
                exchange="events",           # Name of the exchange
                exchange_type="topic",       # Type: topic (uses routing keys)
                durable=True                 # Survives RabbitMQ restarts
            )

            # Connect "documents.extracted" queue to the exchange
            # When someone sends a message with routing_key="documents.extracted",
            # it will arrive in our inbox
            broker.channel.queue_bind(
                exchange="events",
                queue="documents.extracted",
                routing_key="documents.extracted"
            )

            # Connect "documents.indexed" queue to the exchange
            # When we send messages with routing_key="documents.indexed",
            # they'll go to this queue
            broker.channel.queue_bind(
                exchange="events",
                queue="documents.indexed",
                routing_key="documents.indexed"
            )
        logger.info("✅ Queues and exchange configured")
    except Exception as e:
        logger.error(f"❌ Failed to configure queues: {e}")
        sys.exit(1)

    # ========================================================================
    # STEP 3: INITIALIZE INDEXING SERVICE (Load AI Model & Connect to Database)
    # ========================================================================
    # We load the AI model ONCE here (takes ~30 seconds).
    # GLOBAL VARIABLE: We create 'indexing_service' here so the callback
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
    start_health_server(broker, port=8080)

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
            queue_name="documents.extracted",          # Which queue to listen to
            callback=process_document_extracted,       # What function to call for each message
            auto_ack=False                            # We'll manually acknowledge (for reliability)
        )
        # NOTE: The program BLOCKS at the line above! It never reaches this comment
        # until we press Ctrl+C or there's an error.

    except KeyboardInterrupt:
        # User pressed Ctrl+C - shut down gracefully
        logger.info("\n⏹️ Shutting down gracefully...")
        indexing_service.close()  # Close database connections
        broker.close()            # Close RabbitMQ connection
        logger.info("👋 Goodbye!")

    except Exception as e:
        # Something went very wrong - crash and log the error
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        indexing_service.close()
        broker.close()
        sys.exit(1)  # Exit with error code
