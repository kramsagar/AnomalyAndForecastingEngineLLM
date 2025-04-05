from fastapi import FastAPI
import requests
import random
import time
from datetime import datetime

app = FastAPI()

# Splunk HEC Configuration
SPLUNK_HEC_URL = "http://localhost:8088"  # Replace with actual Splunk server
SPLUNK_HEC_TOKEN = "bb71f605-829d-42c3-97fb-d4693940e288"

def send_to_splunk(event):
    """Send event data to Splunk HEC with timing"""
    headers = {
        "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
        "Content-Type": "application/json"
    }

    start_time = time.time()
    # Include response_time_ms in the event before sending
    response = requests.post(
        f"{SPLUNK_HEC_URL}/services/collector",
        headers=headers,
        json={
            "event": event,
            "sourcetype": "_json",
            
            "source": "ms3",
            "index": "cfs_mms"
        }
    )
    end_time = time.time()
    response_time_ms = round((end_time - start_time) * 1000, 2)

    return response.status_code, response.text, response_time_ms

@app.get("/generate")
def generate_transaction():
    """Generate a random dummy transaction and log to Splunk"""
    transaction = {
        "transaction_id": random.randint(100000, 999999),
        "user_id": random.randint(1, 100),
        "amount": round(random.uniform(10.0, 500.0), 2),
        "timestamp": datetime.utcnow().isoformat(),
        "status": random.choice(["SUCCESS", "FAILED", "PENDING"]),
        
        "appid": "app2"
        
    }

    # Measure response time by sending the event
    # But add response_time_ms **before** sending to Splunk
    transaction["response_time_ms"] = None  # Placeholder to keep field order

    # Send transaction (with response_time_ms=None first) to get time
    status_code, response_text, response_time_ms = send_to_splunk({
        **transaction,
        "response_time_ms": None  # Ensure it's included during timing
    })

    # Update the event and re-send with actual response_time_ms
    transaction["response_time_ms"] = response_time_ms
    send_to_splunk(transaction)  # Send the actual transaction with response time

    return {
        "transaction": transaction,
        "splunk_response": response_text,
        "splunk_status": status_code
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
