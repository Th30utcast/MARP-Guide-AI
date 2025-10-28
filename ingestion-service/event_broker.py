import json
import logging
import pika
from typing import Optional

logger = logging.getLogger(__name__)


class RabbitMQEventBroker:
    """Event broker for publishing events to RabbitMQ."""

    def __init__(self, host: str = "localhost", port: int = 5672,
                 username: str = "guest", password: str = "guest"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None

    def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Declare exchange
            self.channel.exchange_declare(
                exchange="events",
                exchange_type="topic",
                durable=True
            )

            # Declare queue
            self.channel.queue_declare(queue="documents.discovered", durable=True)

            # Bind queue to exchange
            self.channel.queue_bind(
                exchange="events",
                queue="documents.discovered",
                routing_key="documents.discovered"
            )

            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    def publish(self, routing_key: str, message: dict, exchange: str = "events"):
        """Publish event to RabbitMQ."""
        if not self.channel:
            self.connect()

        try:
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type="application/json"
                )
            )
            logger.info(f"Published event to {routing_key}: {message.get('eventType', 'unknown')}")

        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}")
            raise

    def close(self):
        """Close connection to RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Closed RabbitMQ connection")
