from kafka import KafkaConsumer
import json
import sys

def get_consumer(topic):
    return KafkaConsumer(
        topic,
        bootstrap_servers=['kafka:9093'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest'
    )

def consume_messages(topic):
    consumer = get_consumer(topic)
    
    for message in consumer:
        try:
            if not message.value:  # Check if the message is empty
                print("Received empty message")
                continue
            
            if not isinstance(message.value, dict):
                print(f"Unexpected message format: {message.value}")
                continue
            
            # Process the message
            task = message.value.get('task_data')
            
            if task is None:
                print(f"Received incomplete message: {message.value}")
                continue

            print(f"Received Task: {task}")
        
        except json.JSONDecodeError as e:
            print(f"Error decoding message: {e}")
            print(f"Raw message: {message.value}")





if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: consumer.py task_topic")
        sys.exit(1)
    
    topic = sys.argv[1]
    consume_messages(topic)