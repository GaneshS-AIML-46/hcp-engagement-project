
# ============================================================
# AgentKF - INTEGRATION TEST
# ============================================================

import sys
from pathlib import Path


PROJECT_DIR = Path(
    __file__
).resolve().parents[1]


sys.path.insert(
    0,
    str(PROJECT_DIR)
)


from agent.workflow import AgentWorkflow


def test_complete_agent_pipeline():

    hcp_data = [

        {
            "hcp_id": "HCP001",
            "name": "Test HCP",
            "specialty": "Oncology"
        }

    ]


    history_data = [

        {
            "hcp_id": "HCP001",
            "channel": "Email",
            "successful": True
        },

        {
            "hcp_id": "HCP001",
            "channel": "Phone",
            "successful": False
        }

    ]


    channel_data = [

        {
            "hcp_id": "HCP001",
            "channel": "Email",
            "probability": 0.85
        },

        {
            "hcp_id": "HCP001",
            "channel": "Phone",
            "probability": 0.55
        }

    ]


    agent = AgentWorkflow(

        hcp_data=hcp_data,

        history_data=history_data,

        channel_data=channel_data,

        memory_database=str(
            PROJECT_DIR
            / "integration_test.db"
        ),

        enable_local_ai=False

    )


    result = agent.run(

        hcp_id="HCP001",

        objective=(
            "Find the best engagement action."
        )

    )


    assert result is not None

    assert "decision" in result

    assert "critic" in result

    assert "explanation" in result

    assert "memory" in result
