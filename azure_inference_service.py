"""
Azure Inference Service for HCP Channel Prediction Model
Provides a lightweight REST API wrapper around hcp_channel_ml_model.pkl
ready for deployment on Azure App Service / Azure Container Instances / Azure ML Endpoints.
"""

import os
import pickle
import joblib
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np


app = FastAPI(
    title="HCP Channel ML Recommendation Model (Azure Hosted)",
    description="Azure REST inference service hosting pickled Calibrated Random Forest model",
    version="1.0.0",
)

MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "hcp_channel_ml_model.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.pkl"

model = None
metadata = None


@app.on_event("startup")
def load_model():
    global model, metadata
    if not MODEL_PATH.exists() or not METADATA_PATH.exists():
        print(f"Warning: Model file not found at {MODEL_PATH}. Run train_and_export_model.py first.")
        return
    model = joblib.load(MODEL_PATH)
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
    print(f"Successfully loaded model from {MODEL_PATH}")


class InferenceInput(BaseModel):
    candidate_channel: str = Field(..., example="email")
    email_freq: float = Field(0.0)
    email_success_rate: float = Field(0.0)
    email_recency_days: Optional[float] = Field(None)
    email_has_history: int = Field(0)
    webinar_freq: float = Field(0.0)
    webinar_success_rate: float = Field(0.0)
    webinar_recency_days: Optional[float] = Field(None)
    webinar_has_history: int = Field(0)
    rep_visit_freq: float = Field(0.0)
    rep_visit_success_rate: float = Field(0.0)
    rep_visit_recency_days: Optional[float] = Field(None)
    rep_visit_has_history: int = Field(0)
    digital_ad_freq: float = Field(0.0)
    digital_ad_success_rate: float = Field(0.0)
    digital_ad_recency_days: Optional[float] = Field(None)
    digital_ad_has_history: int = Field(0)
    phone_call_freq: float = Field(0.0)
    phone_call_success_rate: float = Field(0.0)
    phone_call_recency_days: Optional[float] = Field(None)
    phone_call_has_history: int = Field(0)
    channel_diversity: int = Field(0)
    specialty: Optional[str] = Field("Oncology")
    segment: Optional[str] = Field("High Value")


class BatchInferenceInput(BaseModel):
    instances: List[InferenceInput]


@app.get("/")
def root():
    return {
        "service": "Azure HCP Channel ML Model Service",
        "status": "ready" if model is not None else "model_not_loaded",
        "model_file": str(MODEL_PATH),
    }


@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}


@app.post("/predict")
def predict(payload: BatchInferenceInput):
    if model is None or metadata is None:
        raise HTTPException(status_code=500, detail="ML model is not loaded on Azure server.")

    raw_df = pd.DataFrame([item.dict() for item in payload.instances])
    feature_columns = metadata["feature_columns"]
    train_columns = metadata["train_columns"]

    # Re-encode features to match training feature matrix
    X_input = (
        pd.get_dummies(raw_df.reindex(columns=feature_columns), dummy_na=True)
        .reindex(columns=train_columns, fill_value=0)
        .replace([np.inf, -np.inf], np.nan)
    )

    probabilities = model.predict_proba(X_input)[:, 1]
    
    results = []
    for idx, prob in enumerate(probabilities):
        results.append({
            "candidate_channel": raw_df.iloc[idx]["candidate_channel"],
            "success_probability": round(float(prob), 4),
            "percentage": f"{round(float(prob) * 100, 2)}%"
        })

    return {"predictions": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
