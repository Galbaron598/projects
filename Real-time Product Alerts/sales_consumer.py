from kafka import KafkaConsumer, KafkaProducer
import redis, json, time, uuid
from datetime import datetime, timezone

# Connect to Redis
r = redis.Redis(host="redis", port=6379, db=0)

# Kafka Consumer (sales topic)
consumer = KafkaConsumer(
    "sales",
    bootstrap_servers="kafka:29092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
)

# Kafka Producer (for alerts)
producer = KafkaProducer(
    bootstrap_servers="kafka:29092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

THRESHOLD = 100
WINDOW_SECONDS = 300  # 5 min

for msg in consumer:
    event = msg.value
    product_id = event["product_id"]
    qty = event["quantity"]
    now = int(time.time())

    # Update rolling counter in Redis
    key = f"sales:{product_id}:{now // WINDOW_SECONDS}"
    r.incrby(key, qty)
    r.expire(key, WINDOW_SECONDS * 2)

    # Aggregate sales in last 5 min
    total = 0
    for window in range((now // WINDOW_SECONDS) - 1, (now // WINDOW_SECONDS) + 1):
        val = r.get(f"sales:{product_id}:{window}")
        total += int(val) if val else 0

    # If threshold breached → send alert event to Kafka
    if total > THRESHOLD:
        alert_event = {
            "alert_id": str(uuid.uuid4()),
            "product_id": product_id,
            "total_sales_last_5m": total,
            "threshold": THRESHOLD,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        producer.send("alerts", alert_event)
        print("⚠️ Sent alert event:", alert_event)
