"""
Indexing Service Worker - RabbitMQ Event Consumer Entry Point

Main entry point for the Indexing microservice. This worker process listens for
DocumentExtracted events, performs chunking and embedding, and publishes ChunksIndexed events.

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
import logging
import os
import sys
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler


current_dir = Path(__file__).resolve().parent
project_root = current_dir
sys.path.insert(0, str(project_root))

from common.mq import RabbitMQEventBroker
from indexing_service import IndexingService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks."""

    broker = None

    def do_GET(self):
        """Handle GET requests to /health endpoint."""
        if self.path == '/health':
            # Check if broker is connected
            is_healthy = (
                self.broker is not None and
                self.broker.connection is not None and
                not self.broker.connection.is_closed and
                self.broker.channel is not None and
                self.broker.channel.is_open
            )

            if is_healthy:
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
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default HTTP server logging."""
        pass


def start_health_server(broker, port=8080):
    """
    Start a lightweight HTTP health check server in a background thread.
    Run health check on port 8080
    """

    HealthCheckHandler.broker = broker

    def run_server():
        try:
            server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
            logger.info(f"✅ Health check server started on port {port}")
            server.serve_forever()
        except Exception as e:
            logger.error(f"❌ Failed to start health server: {e}")

    # Run server in daemon thread so it doesn't block shutdown
    health_thread = threading.Thread(target=run_server, daemon=True)
    health_thread.start()


def process_document_extracted(ch, method, properties, body):
    """Callback for processing DocumentExtracted events."""
    try:
        # Decode the message body
        event = json.loads(body)

        # Validate event structure
        if "payload" not in event or "documentId" not in event.get("payload", {}):
            logger.error(f"❌ Invalid event structure: {event}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        logger.info(f"📥 Received DocumentExtracted: {event['payload']['documentId']}")

        # Process the event (chunking, embedding, indexing)
        indexing_service.handle_document_extracted_event(event)

        logger.info(f"✅ Indexed: {event['payload']['documentId']}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing error: {e}")
        logger.error(f"Body content: {body}")

        # Don't requeue malformed messages
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}", exc_info=True)
        # Requeue for retry on transient failures
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


if __name__ == "__main__":
    logger.info("🚀 Initializing Indexing Service Worker...")

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
        broker.declare_queue("documents.extracted")
        broker.declare_queue("documents.indexed")

        if broker.channel:
            broker.channel.exchange_declare(
                exchange="events",
                exchange_type="topic",
                durable=True
            )
            broker.channel.queue_bind(
                exchange="events",
                queue="documents.extracted",
                routing_key="documents.extracted"
            )
            broker.channel.queue_bind(
                exchange="events",
                queue="documents.indexed",
                routing_key="documents.indexed"
            )
        logger.info("✅ Queues and exchange configured")
    except Exception as e:
        logger.error(f"❌ Failed to configure queues: {e}")
        sys.exit(1)

    # Initialize indexing service
    try:
        indexing_service = IndexingService()
        logger.info("✅ Indexing service initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize indexing service: {e}", exc_info=True)
        logger.info("💡 Make sure Qdrant is running: docker-compose up -d qdrant")
        sys.exit(1)

    # Start health check server
    start_health_server(broker, port=8080)

    logger.info("👂 Listening for DocumentExtracted events...")
    logger.info("Press Ctrl+C to stop")

    try:
        broker.consume(
            queue_name="documents.extracted",
            callback=process_document_extracted,
            auto_ack=False
        )
    except KeyboardInterrupt:
        logger.info("\n⏹️ Shutting down gracefully...")
        indexing_service.close()
        broker.close()
        logger.info("👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        indexing_service.close()
        broker.close()
        sys.exit(1)
