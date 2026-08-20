
# ============================================================
# AgentKF - AGENT PLANNER
# ============================================================

class AgentPlanner:
    """
    The Planner decides what steps the Agent
    should perform to solve a user request.
    """

    def __init__(self):

        self.agent_name = "AgentKF Decision Agent"

    def create_plan(self, objective):
        """
        Convert a user objective into a sequence of steps.
        """

        plan = [

            {
                "step": 1,
                "name": "get_hcp_profile",
                "description": "Retrieve the HCP profile."
            },

            {
                "step": 2,
                "name": "get_engagement_history",
                "description": "Retrieve previous engagement history."
            },

            {
                "step": 3,
                "name": "get_channel_scores",
                "description": "Retrieve predicted channel performance."
            },

            {
                "step": 4,
                "name": "analyze_behavior",
                "description": "Analyze engagement behavior."
            },

            {
                "step": 5,
                "name": "select_next_best_action",
                "description": "Select the most suitable next action."
            },

            {
                "step": 6,
                "name": "critic_check",
                "description": "Check the proposed decision."
            },

            {
                "step": 7,
                "name": "generate_response",
                "description": "Prepare the final Agent response."
            }

        ]

        return {
            "agent": self.agent_name,
            "objective": objective,
            "total_steps": len(plan),
            "plan": plan
        }


# Create Planner object
planner = AgentPlanner()
