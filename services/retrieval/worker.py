import json
import logging
from common.config import get_rabbitmq_broker
from common.events import ROUTING_KEY_RETRIEVAL_COMPLETED

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
    broker = get_rabbitmq_broker()

    # Ensure queue and binding exist
    if broker.channel:
        broker.channel.exchange_declare(exchange="events", exchange_type="topic", durable=True)
        broker.channel.queue_declare(queue=ROUTING_KEY_RETRIEVAL_COMPLETED, durable=True)
        broker.channel.queue_bind(exchange="events", queue=ROUTING_KEY_RETRIEVAL_COMPLETED, routing_key=ROUTING_KEY_RETRIEVAL_COMPLETED)

    logger.info(f"Listening on queue '{ROUTING_KEY_RETRIEVAL_COMPLETED}'...")
    broker.consume(queue_name=ROUTING_KEY_RETRIEVAL_COMPLETED, callback=on_message, auto_ack=False)

