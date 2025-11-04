import os
import json
import logging
from common.mq import RabbitMQEventBroker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def on_message(ch, method, properties, body):
    try:
        event = json.loads(body)
        print(json.dumps(event, indent=2))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Failed to process message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


if __name__ == "__main__":
    broker = RabbitMQEventBroker(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        username=os.getenv("RABBITMQ_USER", "guest"),
        password=os.getenv("RABBITMQ_PASSWORD", "guest"),
    )

    # Ensure queue and binding exist
    if broker.channel:
        broker.channel.exchange_declare(exchange="events", exchange_type="topic", durable=True)
        broker.channel.queue_declare(queue="retrieval.completed", durable=True)
        broker.channel.queue_bind(exchange="events", queue="retrieval.completed", routing_key="retrieval.completed")

    logger.info("Listening on queue 'retrieval.completed'...")
    broker.consume(queue_name="retrieval.completed", callback=on_message, auto_ack=False)

