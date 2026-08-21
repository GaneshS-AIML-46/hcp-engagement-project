# ============================================================
# ROOT BACKEND RUNNER FOR DEPLOYMENT / LOCAL LAUNCH
# ============================================================

import os
import sys
from pathlib import Path

# Add current folder to Python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting AgentKF Backend API on port {port}...")
    uvicorn.run(
        "AgentKF_Final.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
