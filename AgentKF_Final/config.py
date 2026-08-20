# ============================================================
# AgentKF - CONFIGURATION
# ============================================================

from pathlib import Path

# ------------------------------------------------------------
# Project Root & Data
# ------------------------------------------------------------

PROJECT_DIR = Path(r"c:\Users\GANESH\Desktop\weight")
AGENT_DIR = PROJECT_DIR / "AgentKF_Final"

DATA_DIR = PROJECT_DIR
INPUT_DIR = PROJECT_DIR
PROCESSED_DIR = PROJECT_DIR

# ------------------------------------------------------------
# Memory
# ------------------------------------------------------------

MEMORY_DATABASE = AGENT_DIR / "agent_memory.db"

# ------------------------------------------------------------
# Local AI / LLM
# ------------------------------------------------------------

LOCAL_AI_MODEL = "google/flan-t5-small"
LOCAL_AI_ENABLED = True

# ------------------------------------------------------------
# API Server
# ------------------------------------------------------------

API_HOST = "0.0.0.0"
API_PORT = 8080
