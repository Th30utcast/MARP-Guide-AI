"""
Common Health Check Module

Provides reusable HTTP health check server for microservices.
Used by worker processes to report their health status to Docker/Kubernetes.

Health checks verify:
- RabbitMQ connection status (broker.connection and broker.channel)
- Returns 200 (healthy) or 503 (unhealthy)
- Runs in background thread (daemon=True) so it doesn't block shutdown

Usage:
    from common.health import start_health_server

    broker = RabbitMQEventBroker(...)
    start_health_server(broker, service_name="my-service", port=8080)
"""

import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional

logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    # Class variables set by start_health_server()
    broker = None
    service_name = "service"

    def do_GET(self):
        # Handle GET requests to /health endpoint.
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
                    "service": self.service_name,
                    "rabbitmq": "connected"
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "unhealthy",
                    "service": self.service_name,
                    "rabbitmq": "disconnected"
                }
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default HTTP server logging (too noisy).
        pass


def start_health_server(broker, service_name: str = "service", port: int = 8080):
    # Configure the handler with broker and service name
    HealthCheckHandler.broker = broker
    HealthCheckHandler.service_name = service_name

    def run_server():
        # Background thread function that runs the HTTP server.
        try:
            server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
            logger.info(f"✅ Health check server started on port {port}")
            server.serve_forever()
        except Exception as e:
            logger.error(f"❌ Failed to start health server: {e}")

    # Start server in daemon thread (dies when main process exits)
    health_thread = threading.Thread(target=run_server, daemon=True)
    health_thread.start()
