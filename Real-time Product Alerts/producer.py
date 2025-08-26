import json
import time
import uuid
import random
from datetime import datetime, timezone
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="kafka:29092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

products = ["p1", "p2", "p3", "p4"]

def generate_sale_event():
    return {
        "event_id": str(uuid.uuid4()),
        "product_id": random.choice(products),
        "quantity": random.randint(1, 5),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

while True:
    event = generate_sale_event()
    producer.send("sales", event)
    producer.flush()
    print("Produced:", event)
    time.sleep(1)  # 1 event per second
