*Real-Time Sales & Alerts System*

This project demonstrates a real-time event pipeline using Kafka, Redis, FastAPI, Node.js, and React.
The flow is:

1. Producer (Python) → generates random sales events and pushes them to Kafka.

2. Sales Consumer (Python) → consumes sales, aggregates counts in Redis, and pushes alerts to Kafka when thresholds are breached.

3. Alert Consumer (Node.js) → consumes alerts from Kafka and stores them in Redis (last 100 alerts).

4. Alert Service API (Python/FastAPI) → exposes /alerts endpoint to fetch alerts from Redis.

5. React UI → fetches alerts via API and displays them in real time.

*Prerequisites - Docker && Docker Compose*

*Run*
in the command line run "docker-compose up --build" 
this will start the services:

Kafka → localhost:9092
Redis → localhost:6379
FastAPI (Alert Service) → http://localhost:4000/alerts
React UI → http://localhost:3000 (open to see the alerts)

*Alert Logic*

Sales events are produced 1 per second.
A rolling 5-minute window is tracked per product.
If sales exceed 100 units in that window → an alert is generated.
Alerts are stored in Redis and displayed in the UI.



*Example Flow*
1. Sales Producer generates sales like:
{
  "event_id": "1234",
  "product_id": "p2",
  "quantity": 5,
  "timestamp": "2025-08-26T12:00:00Z"
}

2. Sales Consumer aggregates totals in Redis.

3. If sales > 100 per 5 minutes, an alert is triggered like this: 
{
  "alert_id": "abcd",
  "product_id": "p2",
  "total_sales_last_5m": 120,
  "threshold": 100,
  "timestamp": "2025-08-26T12:05:00Z"
}

4. Alert Consumer pushes alert into Redis.

5. FastAPI exposes /alerts API with the latest alerts.

6. React UI displays alerts in real time.


Open http://localhost:3000 to see alerts.

To shut down all containers run this command "docker compose down" 





