
# ============================================================
# AgentKF - BASIC TESTS
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


TEST_HCP_DATA = [

    {
        "hcp_id": "HCP001",
        "name": "Arun Kumar",
        "specialty": "Oncology",
        "preferred_channel": "Email"
    }

]


TEST_HISTORY_DATA = [

    {
        "hcp_id": "HCP001",
        "channel": "Email",
        "successful": True
    }

]


TEST_CHANNEL_DATA = [

    {
        "hcp_id": "HCP001",
        "channel": "Email",
        "probability": 0.82
    }

]


def test_agent_creation():

    agent = AgentWorkflow(

        hcp_data=TEST_HCP_DATA,

        history_data=TEST_HISTORY_DATA,

        channel_data=TEST_CHANNEL_DATA,

        memory_database=str(
            PROJECT_DIR
            / "test_memory.db"
        ),

        enable_local_ai=False

    )

    assert agent is not None


def test_agent_run():

    agent = AgentWorkflow(

        hcp_data=TEST_HCP_DATA,

        history_data=TEST_HISTORY_DATA,

        channel_data=TEST_CHANNEL_DATA,

        memory_database=str(
            PROJECT_DIR
            / "test_memory.db"
        ),

        enable_local_ai=False

    )


    result = agent.run(

        hcp_id="HCP001",

        objective=(
            "Find the best engagement action."
        )

    )


    assert "decision" in result

    assert "critic" in result

    assert "explanation" in result
