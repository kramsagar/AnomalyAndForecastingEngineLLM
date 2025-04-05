from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model_trainer import TrainModel
from anomaly_detector import AnomalyDetector

app = FastAPI()

class TrainRequest(BaseModel):
    index_source_appid: str
    metric_type: str
    duration: str

class AnomalyRequest(BaseModel):
    index_source_appid: str
    metric_type: str
    duration: str

@app.post("/train")
def start_training(request: TrainRequest):
    if request.metric_type not in ["volume", "latency"]:
        raise HTTPException(status_code=400, detail="Invalid metric_type")
    return TrainModel.run_in_background(request.index_source_appid, request.metric_type, request.duration)

@app.post("/detect-anomaly")
def detect_anomaly(request: AnomalyRequest):
    if request.metric_type not in ["volume", "latency"]:
        raise HTTPException(status_code=400, detail="Invalid metric_type")
    return AnomalyDetector.detect(request.index_source_appid, request.metric_type, request.duration)
