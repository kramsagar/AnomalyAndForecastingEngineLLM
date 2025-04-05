# tools.py
import requests
from langchain.tools import Tool
from parser import parse_prompt

FASTAPI_URL = "http://localhost:8099"

def train_model(input_str):
    parsed = parse_prompt(input_str)

    if "error" in parsed:
        return f"❌ LLM Parsing Error: {parsed['error']}"

    missing_fields = parsed.get("missing", [])
    if missing_fields:
        return f"⚠️ Missing required fields: {', '.join(missing_fields)}.\nPlease include them in your query. Format: `<app_id>, <metric_type>, <duration>`"

    app_id = parsed["app_id"]
    metric = parsed["metric_type"]
    duration = parsed["duration"]

    payload = {
        "index_source_appid": app_id,
        "metric_type": metric,
        "duration": duration
    }

    try:
        response = requests.post(f"{FASTAPI_URL}/train", json=payload)
        response.raise_for_status()
        return f"✅ Training started successfully.\n🧠 Response: {response.text}"
    except Exception as e:
        return f"❌ Training failed: {str(e)}"

def detect_anomaly(input_str):
    parsed = parse_prompt(input_str)

    if "error" in parsed:
        return f"❌ LLM Parsing Error: {parsed['error']}"

    missing_fields = parsed.get("missing", [])
    if missing_fields:
        return f"⚠️ Missing required fields: {', '.join(missing_fields)}.\nPlease include them in your query. Format: `<app_id>, <metric_type>, <duration>`"

    app_id = parsed["app_id"]
    metric = parsed["metric_type"]
    duration = parsed["duration"]

    payload = {
        "index_source_appid": app_id,
        "metric_type": metric,
        "duration": duration
    }

    try:
        response = requests.post(f"{FASTAPI_URL}/detect-anomaly", json=payload)
        response.raise_for_status()
        return f"✅ Anomaly detection complete.\n📊 Response: {response.text}"
    except Exception as e:
        return f"❌ Anomaly detection failed: {str(e)}"

train_model_tool = Tool.from_function(
    name="train_model_tool",
    func=train_model,
    description="Train the anomaly detection model. Input should include app ID, metric type (e.g. volume/latency), and duration like '2hr' or '30min'."
)

detect_anomaly_tool = Tool.from_function(
    name="detect_anomaly_tool",
    func=detect_anomaly,
    description="Detect anomalies. Input should include app ID, metric type (e.g. latency), and duration like '1hr'."
)
