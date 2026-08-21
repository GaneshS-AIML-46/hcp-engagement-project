# ============================================================
# AgentKF - FASTAPI BACKEND WITH REAL ENTROPY SCORING & ML MODEL
# ============================================================

import sys
import pickle
import joblib
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np


# Setup project paths
API_FILE_DIR = Path(__file__).parent
AGENT_DIR = API_FILE_DIR.parent
PROJECT_DIR = AGENT_DIR.parent

if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from agent.workflow import AgentWorkflow


# ============================================================
# LOAD REAL PIPELINE DATASETS & ML PICKLE MODEL
# ============================================================

ENTROPY_CSV = PROJECT_DIR / "HCP_Entropy_and_ML_Recommendations.csv"
ML_RECS_CSV = PROJECT_DIR / "HCP_ML_Channel_Recommendations.csv"
HISTORY_CSV = PROJECT_DIR / "Engagement_history_improved.csv"
MODEL_PKL = PROJECT_DIR / "models" / "hcp_channel_ml_model.pkl"
METADATA_PKL = PROJECT_DIR / "models" / "model_metadata.pkl"


def load_datasets():
    if not ENTROPY_CSV.exists():
        # Fallback to run pipeline if not pre-computed
        from pipeline import run_pipeline
        entropy_df, ml_recs_df = run_pipeline()
    else:
        entropy_df = pd.read_csv(ENTROPY_CSV)
        ml_recs_df = pd.read_csv(ML_RECS_CSV) if ML_RECS_CSV.exists() else None

    history_df = pd.read_csv(HISTORY_CSV) if HISTORY_CSV.exists() else None
    
    ml_model = None
    ml_metadata = None
    if MODEL_PKL.exists() and METADATA_PKL.exists():
        try:
            ml_model = joblib.load(MODEL_PKL)
            with open(METADATA_PKL, "rb") as f:
                ml_metadata = pickle.load(f)
        except Exception as e:
            print(f"Could not load ML model: {e}")

    return entropy_df, ml_recs_df, history_df, ml_model, ml_metadata


entropy_df, ml_recs_df, history_df, ml_model, ml_metadata = load_datasets()


# Standardize channel display names
CHANNEL_DISPLAY_MAP = {
    "rep_visit": "Rep Visit",
    "phone_call": "Phone Call",
    "webinar": "Webinar",
    "email": "Email",
    "digital_ad": "Digital Ad",
}

REVERSE_CHANNEL_MAP = {v: k for k, v in CHANNEL_DISPLAY_MAP.items()}


# Prepare Agent Workflow adapter data
def build_agent_data():
    hcp_data_records = []
    channel_data_records = []
    history_records = []

    for _, row in entropy_df.iterrows():
        hcp_id = str(row["hcp_id"])
        name = f"Dr. {row.get('first_name', '')} {row.get('last_name', '')}".strip()
        if name == "Dr.":
            name = f"Dr. HCP #{hcp_id}"
            
        hcp_data_records.append({
            "hcp_id": hcp_id,
            "name": name,
            "specialty": str(row.get("specialty", "General Medicine")),
            "location": str(row.get("territory", "Metro")),
            "segment": str(row.get("segment", "Tier 1")),
            "preferred_channel": CHANNEL_DISPLAY_MAP.get(str(row.get("recommended_channel")), str(row.get("recommended_channel"))),
            "entropy_score": float(row.get("entropy_weighted_score", 0)),
        })

    if ml_recs_df is not None:
        for _, row in ml_recs_df.iterrows():
            channel_data_records.append({
                "hcp_id": str(row["hcp_id"]),
                "channel": CHANNEL_DISPLAY_MAP.get(str(row["candidate_channel"]), str(row["candidate_channel"])),
                "probability": float(row.get("success_probability", 0)),
                "tier": str(row.get("recommendation_tier", "Other")),
            })

    if history_df is not None:
        for _, row in history_df.iterrows():
            history_records.append({
                "hcp_id": str(row["hcp_id"]),
                "channel": CHANNEL_DISPLAY_MAP.get(str(row["channel"]), str(row["channel"])),
                "successful": bool(row.get("engagement_successful", False)),
                "date": str(row.get("engagement_date", "")),
            })

    return hcp_data_records, history_records, channel_data_records


hcp_records, history_records, channel_records = build_agent_data()

agent = AgentWorkflow(
    hcp_data=hcp_records,
    history_data=history_records,
    channel_data=channel_records,
    memory_database=str(AGENT_DIR / "agent_memory.db"),
    enable_local_ai=True,
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AgentKF API - Omnichannel Engagement & ML Recommendation",
    description="Backend API providing real Entropy Engagement Scores and Azure-ready ML Pickle Recommendations",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST & RESPONSE MODELS
# ============================================================

class AgentRequest(BaseModel):
    hcp_id: str = Field(..., description="HCP identifier")
    objective: str = Field(..., description="Agent objective")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User question or query")


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {
        "status": "Backend is working",
        "service": "AgentKF Omnichannel Scoring API",
        "scoring_model": "Dynamic Shannon Entropy (No Arbitrary Weights)",
        "ml_model_loaded": ml_model is not None,
        "total_hcps": len(entropy_df),
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/agent/health")
def health():
    return {
        "status": "healthy",
        "agent": "AgentKF",
        "entropy_model": True,
        "ml_pickle_model": ml_model is not None,
        "local_ai": agent.local_ai_available,
    }


@app.get("/api/stats")
def get_stats():
    scores = entropy_df["entropy_weighted_score"].dropna()
    total = len(entropy_df)
    avg_score = float(scores.mean().round(2)) if total > 0 else 0.0
    
    opted_out = int(entropy_df["opt_out_flag"].fillna(False).sum()) if "opt_out_flag" in entropy_df.columns else 0
    eligible = total - opted_out

    high = int((scores >= 40).sum())
    moderate = int(((scores >= 20) & (scores < 40)).sum())
    low = int(((scores >= 1) & (scores < 20)).sum())
    disengaged = int((scores == 0).sum())

    top_ch = str(entropy_df["recommended_channel"].value_counts().idxmax())
    top_channel_display = CHANNEL_DISPLAY_MAP.get(top_ch, top_ch)

    return {
        "total_hcps": total,
        "eligible_hcps": eligible,
        "opted_out": opted_out,
        "avg_engagement_score": avg_score,
        "top_channel": top_channel_display,
        "engaged_hcps": high + moderate,
        "highly_engaged_hcps": high,
        "moderately_engaged_hcps": moderate,
        "low_engaged_hcps": low,
        "low_engagement_hcps": low,
        "disengaged_hcps": disengaged,
    }


@app.get("/api/hcps")
def get_all_hcps():
    results = []
    for _, row in entropy_df.sort_values("entropy_weighted_score", ascending=False).iterrows():
        hcp_id = str(row["hcp_id"])
        first_name = str(row.get("first_name", "Doctor"))
        last_name = str(row.get("last_name", f"#{hcp_id}"))
        doctor_name = f"Dr. {first_name} {last_name}".strip()
        
        score = float(row.get("entropy_weighted_score", 0))
        rec_ch = str(row.get("recommended_channel", "email"))
        rec_ch_display = CHANNEL_DISPLAY_MAP.get(rec_ch, rec_ch)

        results.append({
            "hcp_id": hcp_id,
            "first_name": first_name,
            "last_name": last_name,
            "doctor_name": doctor_name,
            "specialty": str(row.get("specialty", "General")),
            "segment": str(row.get("segment", "Tier 1")),
            "overall_engagement_score_100": score,
            "overall_engagement_score": score,
            "entropy_rank": int(row.get("entropy_weighted_rank", 0)),
            "recommended_channel": rec_ch_display,
            "preferred_channel": rec_ch_display,
            "opt_out_flag": bool(row.get("opt_out_flag", False)),
        })
    return results


@app.get("/api/hcp/{hcp_id}")
def get_hcp_detail(hcp_id: str):
    # Find HCP row
    match = entropy_df.loc[entropy_df["hcp_id"].astype(str).eq(str(hcp_id))]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"HCP '{hcp_id}' not found.")

    row = match.iloc[0]
    score = float(row.get("entropy_weighted_score", 0))
    first_name = str(row.get("first_name", "Doctor"))
    last_name = str(row.get("last_name", f"#{hcp_id}"))
    doctor_name = f"Dr. {first_name} {last_name}".strip()
    specialty = str(row.get("specialty", "General Specialty"))
    segment = str(row.get("segment", "Medium Value"))

    rec_ch = str(row.get("recommended_channel", "email"))
    rec_ch_display = CHANNEL_DISPLAY_MAP.get(rec_ch, rec_ch)

    # Extract individual entropy channel scores (0-1)
    channel_scores = {}
    total_entropy_ch_sum = 0.0
    for ch_raw, ch_display in CHANNEL_DISPLAY_MAP.items():
        col = f"entropy_channel_score_{ch_raw}"
        val = float(row.get(col, 0)) if col in row else 0.0
        channel_scores[ch_display] = round(val, 3)
        total_entropy_ch_sum += val

    # Calculate weighted contributions (proportions)
    weighted_contributions = {}
    for ch_display, val in channel_scores.items():
        prop = (val / total_entropy_ch_sum) if total_entropy_ch_sum > 0 else 0.20
        weighted_contributions[ch_display] = round(prop, 3)

    # ML Channel Predictions for this HCP
    ml_recs = []
    if ml_recs_df is not None:
        hcp_ml = ml_recs_df.loc[ml_recs_df["hcp_id"].astype(str).eq(str(hcp_id))].sort_values("success_probability", ascending=False)
        for _, ml_row in hcp_ml.iterrows():
            ch_raw = str(ml_row["candidate_channel"])
            ml_recs.append({
                "channel": CHANNEL_DISPLAY_MAP.get(ch_raw, ch_raw),
                "probability": float(ml_row.get("success_probability", 0)),
                "tier": str(ml_row.get("recommendation_tier", "Other")),
            })

    top_ml_ch = ml_recs[0]["channel"] if ml_recs else rec_ch_display

    return {
        "hcp_id": str(hcp_id),
        "doctor_name": doctor_name,
        "first_name": first_name,
        "last_name": last_name,
        "specialty": specialty,
        "segment": segment,
        "overall_engagement_score": score,
        "overall_engagement_score_100": score,
        "entropy_weighted_rank": int(row.get("entropy_weighted_rank", 0)),
        "recommended_channel": rec_ch_display,
        "preferred_channel": rec_ch_display,
        "ml_primary_channel": top_ml_ch,
        "channel_scores": channel_scores,
        "weighted_contributions": weighted_contributions,
        "ml_channel_recommendations": ml_recs,
    }


@app.post("/api/chat")
def chat_bot(request: ChatRequest):
    query = request.message.strip().lower()

    # Search for HCP ID in query
    found_id = None
    import re
    id_matches = re.findall(r'\b\d+\b', query)
    if id_matches:
        for possible_id in id_matches:
            if any(str(h["hcp_id"]) == str(possible_id) for h in hcp_records):
                found_id = str(possible_id)
                break

    if found_id:
        # Run agent workflow for specific HCP
        result = agent.run(
            hcp_id=found_id,
            objective=f"Answer question for HCP {found_id}: {request.message}"
        )
        hcp_info = next(h for h in hcp_records if str(h["hcp_id"]) == found_id)
        
        reply = (
            f"📊 **HCP #{found_id} ({hcp_info['name']}) Insights**:\n\n"
            f"• **Engagement Score**: **{hcp_info['entropy_score']:.1f}/100**\n"
            f"• **Recommended Channel**: **{hcp_info['preferred_channel']}**\n"
            f"• **Specialty**: {hcp_info['specialty']} | **Segment**: {hcp_info['segment']}\n\n"
            f"💡 **AI Next Best Action**: {result.get('decision', {}).get('next_best_action', 'Focus on top engagement channel.')}\n\n"
            f"📝 **Explanation**: {result.get('explanation', {}).get('summary', 'High response rate recorded on preferred channel.')}"
        )
        return {"response": reply}

    elif "score" in query or "model" in query or "weight" in query or "entropy" in query:
        top_hcp = max(hcp_records, key=lambda x: x["entropy_score"])
        reply = (
            f"⚙️ **Engagement Score Model Overview**:\n\n"
            f"• Our system computes dynamic **Engagement Scores** across interaction Frequency, Success Rate, and Recency.\n"
            f"• Channel preferences are dynamically assigned based on interaction data.\n"
            f"• **Top Engaged HCP**: #{top_hcp['hcp_id']} ({top_hcp['name']}) with Engagement Score **{top_hcp['entropy_score']:.1f}/100**."
        )
        return {"response": reply}

    elif "azure" in query or "pickle" in query or "ml" in query:
        reply = (
            f"☁️ **ML Model Pickle & Azure Hosting Status**:\n\n"
            f"• **Model File**: `models/hcp_channel_ml_model.pkl` (Calibrated Random Forest Classifier Pipeline)\n"
            f"• **Azure Service Script**: `azure_inference_service.py` is ready for deployment on Azure Web Apps / Azure ML Endpoint.\n"
            f"• **Live Status**: {'Model loaded in backend' if ml_model is not None else 'Model ready to load'}"
        )
        return {"response": reply}

    else:
        # General response
        avg_score = entropy_df["entropy_weighted_score"].mean()
        reply = (
            f"👋 Hello! I am your AI Omnichannel HCP Engagement Assistant.\n\n"
            f"• System total HCPs: **{len(entropy_df)}**\n"
            f"• System Average Engagement Score: **{avg_score:.1f}/100**\n"
            f"• Trained ML Model is serialized as `.pkl` and ready for Azure deployment.\n\n"
            f"Try asking me: *'What is the engagement score for HCP 1?'* or *'Show me top channel recommendations'*."
        )
        return {"response": reply}


@app.post("/api/agent/run")
def run_agent(request: AgentRequest):
    hcp_exists = any(str(h.get("hcp_id")) == str(request.hcp_id) for h in hcp_records)
    if not hcp_exists:
        raise HTTPException(status_code=404, detail=f"HCP '{request.hcp_id}' was not found.")

    try:
        result = agent.run(hcp_id=request.hcp_id, objective=request.objective)
        return result
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/api/agent/memory/{hcp_id}")
def get_memory(hcp_id: str):
    try:
        records = agent.memory.get_history(hcp_id)
        return {"hcp_id": hcp_id, "records": records}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
