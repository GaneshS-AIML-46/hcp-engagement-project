# AgentKF Handoff

## What this is

AgentKF is the standalone Agentic AI component
for the Omnichannel Engagement Scoring project.

## Current capabilities

- Planner
- Data tools
- ML prediction adapter
- Behavioral analysis
- Decision intelligence
- Next Best Action
- Critic / guardrails
- Explanation system
- Free local AI
- Memory
- FastAPI backend
- API validation
- Automated tests

## Important

The AgentKF component is designed to be integrated
with the main project later.

## Current test data

The original development version contains temporary
test data.

For final integration, connect the real project
datasets and ML prediction outputs.

## API

GET /api/agent/health

POST /api/agent/run

GET /api/agent/memory/{hcp_id}

## Run locally

Install dependencies:

pip install -r requirements.txt

Run:

python run.py

API:

http://localhost:8000

Swagger:

http://localhost:8000/docs

## Integration

The frontend should communicate with the FastAPI
backend rather than directly importing AgentKF Python
modules.

## Local AI

AgentKF uses a free local Hugging Face model:

google/flan-t5-small

No OpenAI API key is required.