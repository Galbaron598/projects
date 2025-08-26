from fastapi import FastAPI
import redis
import json

app = FastAPI()

# Connect to Redis
r = redis.Redis(host="redis", port=6379, decode_responses=True)

@app.get("/alerts")
def get_alerts():
    try:
        # Get up to 100 latest alerts
        alerts = r.lrange("alerts", 0, 99)
        parsed_alerts = [json.loads(a) for a in alerts]
        return {"alerts": parsed_alerts}
    except Exception as e:
        return {"error": str(e)}