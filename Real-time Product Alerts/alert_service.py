from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
import json

app = FastAPI()


# Allow CORS for frontend on port 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Redis
r = redis.Redis(host="redis", port=6379)

@app.get("/alerts")
def get_alerts():
    try:
        # Get up to 100 latest alerts
        alerts = r.lrange("alerts", 0, 99)
        parsed_alerts = [json.loads(a) for a in alerts]
        print("DEBUG alerts from Redis:", parsed_alerts)
        return {"alerts": parsed_alerts}
    except Exception as e:
        return {"error": str(e)}