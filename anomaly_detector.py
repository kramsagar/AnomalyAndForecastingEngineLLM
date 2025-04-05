import os
import pickle
from splunk_utils import fetch_splunk_data, get_storage_path
from fastapi import HTTPException
from sklearn.ensemble import IsolationForest
import pandas as pd

class AnomalyDetector:
    @staticmethod
    def detect(index_source_appid, metric_type, duration):
        """Detect anomalies using trained Isolation Forest model."""
        storage_path = get_storage_path(index_source_appid)
        
        model_files = [f for f in os.listdir(storage_path) if f.startswith(metric_type)]
        if not model_files:
            raise HTTPException(status_code=404, detail="No trained model found")

        latest_model = sorted(model_files)[-1]
        model_path = os.path.join(storage_path, latest_model)

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        data = fetch_splunk_data(index_source_appid, metric_type, duration)
        if not data:
            return {"message": "No data available for anomaly detection"}

        metric_field = "txn_count" if metric_type == "volume" else "avg_response_time"
        metric_values = [float(event[metric_field]) for event in data if metric_field in event]

        if not metric_values:
            return {"message": f"No valid {metric_field} values found for anomaly detection"}

        df = pd.DataFrame(metric_values, columns=[metric_field])
        predictions = model.predict(df)

        anomalies = [v for i, v in enumerate(metric_values) if predictions[i] == -1]

        return {
            "index_source_appid": index_source_appid,
            "metric_type": metric_type,
            "anomaly_detected": bool(anomalies),
            "anomaly_values": anomalies,
            "total_checked": len(metric_values),
            "latest_model": latest_model
        }
