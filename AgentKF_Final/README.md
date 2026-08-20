
# AgentKF — Agentic AI Component

AgentKF is an Agentic AI backend component designed
for an Omnichannel Engagement Scoring project.

The component is designed to work independently from
the main project and can later be integrated with the
main application.

---

## Main Components

AgentKF contains:

- Agent Planner
- HCP Data Tools
- Engagement History Analysis
- Channel Analysis
- Decision Intelligence
- Next Best Action
- Critic / Guardrails
- Explanation Generator
- Agent Memory
- Free Local AI
- ML Prediction Adapter
- Data Adapter
- FastAPI Backend

---

## Architecture

User / Frontend

        ↓

FastAPI

        ↓

AgentKF

        ↓

Planner

        ↓

Tools

        ↓

Analysis

        ↓

Decision Intelligence

        ↓

Next Best Action

        ↓

Critic

        ↓

Explanation

        ↓

Memory

---

## Local AI

AgentKF optionally uses:

google/flan-t5-small

through Hugging Face Transformers.

No OpenAI API key is required.

---

## API

### Health

GET

/api/agent/health

---

### Run Agent

POST

/api/agent/run

Example:

{
    "hcp_id": "HCP001",
    "objective": "Find the best engagement action."
}

---

### Memory

GET

/api/agent/memory/{hcp_id}

---

## Project Structure

AgentKF/

    agent/

    api/

    data/

    tests/

    outputs/

    config.py

    run.py

    requirements.txt

    README.md

---

## Installation

Install dependencies:

pip install -r requirements.txt

---

## Run

python run.py

---

## Important

The current version contains temporary test data.

Before final integration, replace the test data
with the actual project data and ML prediction outputs.

---

## Future Integration

The final system will connect:

Main Project

        ↓

ML Models

        ↓

AgentKF

        ↓

Next Best Action

        ↓

Frontend
