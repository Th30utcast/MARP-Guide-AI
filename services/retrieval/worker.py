# The script imports json for parsing JSON, logging for logging, get_rabbitmq_broker from common.config to create a RabbitMQ
# connection, and ROUTING_KEY_RETRIEVAL_COMPLETED from common.events as the queue name.
import json
import logging

from common.config import get_rabbitmq_broker
from common.events import ROUTING_KEY_RETRIEVAL_COMPLETED

# Logging is configured to show INFO-level messages with timestamps and a logger is created for this module.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# on_message handles incoming messages. It parses the JSON body, prints it with indentation,
# then acknowledges the message. If parsing fails, it logs an error and rejects the message without requeueing.
def on_message(ch, method, properties, body):
    try:
        event = json.loads(body)
        print(json.dumps(event, indent=2))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Failed to process message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


# When the script runs, it gets a RabbitMQ broker connection. If the channel exists, it declares a topic exchange
# named "events", declares a durable queue using the routing key constant, and binds the queue to the exchange with that routing key.
# It logs that it's listening, then starts consuming from the queue, calling on_message for each message and not auto-acknowledging.
if __name__ == "__main__":
    broker = get_rabbitmq_broker()

    # Ensure queue and binding exist
    if broker.channel:
        broker.channel.exchange_declare(exchange="events", exchange_type="topic", durable=True)
        broker.channel.queue_declare(queue=ROUTING_KEY_RETRIEVAL_COMPLETED, durable=True)
        broker.channel.queue_bind(
            exchange="events", queue=ROUTING_KEY_RETRIEVAL_COMPLETED, routing_key=ROUTING_KEY_RETRIEVAL_COMPLETED
        )

    logger.info(f"Listening on queue '{ROUTING_KEY_RETRIEVAL_COMPLETED}'...")
    broker.consume(queue_name=ROUTING_KEY_RETRIEVAL_COMPLETED, callback=on_message, auto_ack=False)
