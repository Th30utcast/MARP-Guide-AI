import json
import pika
import logging
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)


class RabbitMQEventBroker:
    # Event broker implementation using RabbitMQ for publishing and consuming events.
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest"
    ):
        self.host = host
        self.port = port
        self.credentials = pika.PlainCredentials(username, password)
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
        
        self._connect()
    
    def _connect(self):
        # Establish connection to RabbitMQ.
        try:
            connection_params = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=self.credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise
    
    def declare_queue(self, queue_name: str, durable: bool = True):
        # queue_name: Name of the queue
        # durable: Whether the queue should survive broker restarts
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")
        
        self.channel.queue_declare(queue=queue_name, durable=durable)
        logger.info(f"Declared queue: {queue_name}")
    
    def publish(self, routing_key: str, message: str, exchange: str = "events"):
        # Publish a message to an exchange.
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")
        
        try:
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                    content_type="application/json"
                )
            )
            logger.info(f"Published message to {exchange}/{routing_key}")
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            raise
    
    def consume(
        self,
        queue_name: str,
        callback: Callable[[Any, Any, Any, bytes], None],
        auto_ack: bool = False
    ):
        """
            queue_name: Queue to consume from
            callback: Callback function (ch, method, properties, body) -> None
            auto_ack: Whether to auto-acknowledge messages
        """
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")
        
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=auto_ack
        )
        
        logger.info(f"Started consuming from queue: {queue_name}")
        self.channel.start_consuming()
    
    def close(self):
        """Close the RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Closed RabbitMQ connection")