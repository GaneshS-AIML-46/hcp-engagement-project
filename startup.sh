#!/bin/bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker AgentKF_Final.api.main:app --bind 0.0.0.0:${PORT:-8000}
