from kafka import KafkaProducer
import json

def get_producer():
    return KafkaProducer(
        bootstrap_servers=['kafka:9093'],
        value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
    )

def produce_message(topic, message):
    producer = get_producer()
    producer.send(topic, message)
    print("Message sent")
    producer.flush()

