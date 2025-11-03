"""
Ingestion Service Worker - Entry Point

Main entry point for the Ingestion microservice. This worker process runs the
ingestion service to discover and fetch PDFs, then publishes DocumentDiscovered events.

Architecture:
    - Worker process (runs ingestion on startup)
    - Connects to RabbitMQ message broker for event publishing
    - Runs HTTP health check server in background thread for monitoring
    - Stateless: Can be run multiple times (will skip already-fetched PDFs)

Health Check:
    - HTTP server on port 8000 (/health endpoint)
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

# Add paths for imports
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from common.mq import RabbitMQEventBroker
from ingestion_service import IngestionService

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
                    "service": "ingestion-service",
                    "rabbitmq": "connected"
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "unhealthy",
                    "service": "ingestion-service",
                    "rabbitmq": "disconnected"
                }
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default HTTP server logging."""
        pass


def start_health_server(broker, port=8000):
    """
    Start a lightweight HTTP health check server in a background thread.
    Run health check on port 8000.
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


if __name__ == "__main__":
    logger.info("🚀 Initializing Ingestion Service Worker...")

    # Environment variables
    MARP_URL = os.getenv(
        "MARP_URL",
        "https://www.lancaster.ac.uk/academic-standards-and-quality/regulations-and-policies/manual-of-academic-regulations-and-procedures/"
    )
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    PDF_OUTPUT_DIR = os.getenv("PDF_OUTPUT_DIR", "/app/pdfs")
    STORAGE_PATH = os.getenv("STORAGE_PATH", "/app/storage/extracted")

    # Initialize event broker
    try:
        broker = RabbitMQEventBroker(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            username=RABBITMQ_USER,
            password=RABBITMQ_PASSWORD
        )
        logger.info("✅ Connected to RabbitMQ")
    except Exception as e:
        logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
        logger.info("💡 Make sure RabbitMQ is running: docker-compose up -d rabbitmq")
        sys.exit(1)

    # Declare queues and exchange
    try:
        broker.declare_queue("documents.discovered")
        broker.declare_queue("documents.ingestion.failed")

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
                queue="documents.ingestion.failed",
                routing_key="documents.ingestion.failed"
            )
        logger.info("✅ Queues and exchange configured")
    except Exception as e:
        logger.error(f"❌ Failed to configure queues: {e}")
        sys.exit(1)

    # Initialize ingestion service
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

    # Start health check server
    start_health_server(broker, port=8000)

    # Run ingestion process
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

    # Keep the process alive for health checks
    logger.info("✅ Ingestion service running. Keeping process alive for health checks...")
    logger.info("Press Ctrl+C to stop")
    try:
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("\n⏹️ Shutting down gracefully...")
        ingestion_service.close()
        broker.close()
        logger.info("👋 Goodbye!")
