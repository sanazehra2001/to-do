from kafka import KafkaProducer
import logging
import json
import os

logger = logging.getLogger('toDoApp')

def get_producer():
    return KafkaProducer(
        bootstrap_servers=[os.getenv('KAFKA_BOOTSTRAP_SERVER')],
        value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
    )

def produce_message(topic, message):
    producer = get_producer()
    producer.send(topic, message)
    logger.debug("Message sent")
    producer.flush()



