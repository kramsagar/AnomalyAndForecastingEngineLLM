import os
import pickle
import threading
import time
from datetime import datetime
from splunk_utils import fetch_splunk_data, get_storage_path, running_models, is_model_running, set_model_status
from sklearn.ensemble import IsolationForest
import pandas as pd

class TrainModel:

    @staticmethod
    def train_model(index_source_appid, metric_type, duration):
            """Train ML model using txn_count or avg_response_time."""
            storage_path = get_storage_path(index_source_appid)
            os.makedirs(storage_path, exist_ok=True)

            if is_model_running(index_source_appid, metric_type):
                return {"message": f"Model training already in progress for {index_source_appid} - {metric_type}"}

            set_model_status(index_source_appid, metric_type, True)

            try:
                data = fetch_splunk_data(index_source_appid, metric_type, duration)
                if not data:
                    return {"message": "No data found for training"}

                metric_field = "txn_count" if metric_type == "volume" else "avg_response_time"
                metric_values = [float(event[metric_field]) for event in data if metric_field in event]

                if not metric_values:
                    return {"message": f"No valid {metric_field} values found for training"}

                # Convert to DataFrame
                df = pd.DataFrame(metric_values, columns=[metric_field])

                # Train Isolation Forest
                model = IsolationForest(contamination=0.05, random_state=42)
                model.fit(df)

                timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H")
                model_filename = f"{metric_type}_model_{timestamp}.pkl"
                model_path = os.path.join(storage_path, model_filename)

                with open(model_path, "wb") as f:
                    pickle.dump(model, f)

                return {"message": f"Model trained and saved: {model_path}"}
            finally:
                set_model_status(index_source_appid, metric_type, False)

    @staticmethod
    def run_in_background(index_source_appid, metric_type, duration):
        thread = threading.Thread(target=TrainModel.train_model, args=(index_source_appid, metric_type, duration))
        thread.start()
        return {"message": f"Training started for {index_source_appid} - {metric_type}"}
