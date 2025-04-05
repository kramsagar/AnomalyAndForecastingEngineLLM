import os
import json
import requests
from typing import List, Dict
from requests.auth import HTTPBasicAuth
from fastapi import HTTPException

SPLUNK_HOST = "https://localhost:8089"
SPLUNK_USERNAME = "rkyasan44"
SPLUNK_PASSWORD = "*****"
SPLUNK_SEARCH_URL = f"{SPLUNK_HOST}/services/search/jobs/export"

BASE_DIR = "microservice3_storage"
running_models = {}  # Track active trainings

def splunk_search_query(index_source_appid: str, metric_type: str, duration: str) -> str:
    time_filter = f"-{duration}"
    metric_field = "txn_count" if metric_type == "volume" else "avg_response_time"
    return f'search index="summary_transactions" earliest_time={time_filter} latest_time=now ' \
           f'index_source_appid="{index_source_appid}" | table _time, index_source_appid, {metric_field}'

def fetch_splunk_data(index_source_appid: str, metric_type: str, duration: str) -> List[Dict]:
    query = splunk_search_query(index_source_appid, metric_type, duration)
    
    print(f"Splunk Query: {query}")

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    auth = HTTPBasicAuth(SPLUNK_USERNAME, SPLUNK_PASSWORD)

    try:
        response = requests.post(
            SPLUNK_SEARCH_URL,
            headers=headers,
            auth=auth,
            data={"search": query, "output_mode": "json"},
            verify=False
        )
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Splunk Error: {response.text}")

        results = []
        for line in response.text.strip().split("\n"):
            if line.strip():
                json_obj = json.loads(line)
                if "result" in json_obj:
                    results.append(json_obj["result"])

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_storage_path(index_source_appid: str):
    return os.path.join(BASE_DIR, index_source_appid)

def is_model_running(index_source_appid: str, metric_type: str):
    return running_models.get(f"{index_source_appid}_{metric_type}", False)

def set_model_status(index_source_appid: str, metric_type: str, status: bool):
    running_models[f"{index_source_appid}_{metric_type}"] = status
