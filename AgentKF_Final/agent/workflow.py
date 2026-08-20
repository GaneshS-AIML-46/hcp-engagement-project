
# ============================================================
# AgentKF - COMPLETE AGENT WORKFLOW
# ============================================================

from agent.planner import AgentPlanner

from agent.tools import (
    HCPProfileTool,
    EngagementHistoryTool,
    ChannelScoreTool
)

from agent.analyzer import AnalysisEngine

from agent.decision import (
    NextBestActionEngine
)

from agent.critic import AgentCritic

from agent.explainer import (
    ExplanationGenerator
)

from agent.intelligence import (
    DecisionIntelligence
)

from agent.memory import (
    AgentMemory
)

from agent.local_ai import (
    LocalAI
)


class AgentWorkflow:

    def __init__(
        self,
        hcp_data,
        history_data,
        channel_data,
        memory_database,
        enable_local_ai=True
    ):

        # ====================================================
        # CORE AGENT COMPONENTS
        # ====================================================

        self.planner = AgentPlanner()

        self.hcp_tool = HCPProfileTool(
            hcp_data
        )

        self.history_tool = (
            EngagementHistoryTool(
                history_data
            )
        )

        self.channel_tool = (
            ChannelScoreTool(
                channel_data
            )
        )

        self.analysis_engine = (
            AnalysisEngine()
        )

        self.decision_engine = (
            NextBestActionEngine()
        )

        self.critic = AgentCritic()

        self.explainer = (
            ExplanationGenerator()
        )

        self.intelligence = (
            DecisionIntelligence()
        )

        self.memory = AgentMemory(
            memory_database
        )


        # ====================================================
        # FREE LOCAL AI
        # ====================================================

        self.local_ai = None

        self.local_ai_available = False


        if enable_local_ai:

            try:

                self.local_ai = LocalAI()

                self.local_ai_available = (
                    self.local_ai.load()
                )

            except Exception as error:

                print(
                    "Local AI unavailable:"
                )

                print(error)

                self.local_ai_available = False


    # ========================================================
    # MAIN AGENT EXECUTION
    # ========================================================

    def run(
        self,
        hcp_id,
        objective
    ):

        # ====================================================
        # 1. PLAN
        # ====================================================

        plan = (
            self.planner.create_plan(
                objective
            )
        )


        # ====================================================
        # 2. HCP PROFILE
        # ====================================================

        hcp_profile = (
            self.hcp_tool.run(
                hcp_id
            )
        )


        # ====================================================
        # 3. ENGAGEMENT HISTORY
        # ====================================================

        engagement_history = (
            self.history_tool.run(
                hcp_id
            )
        )


        # ====================================================
        # 4. CHANNEL SCORES
        # ====================================================

        channel_scores = (
            self.channel_tool.run(
                hcp_id
            )
        )


        # ====================================================
        # 5. ANALYSIS
        # ====================================================

        analysis = (
            self.analysis_engine.analyze(

                engagement_history,

                channel_scores

            )
        )


        # ====================================================
        # 6. DECISION INTELLIGENCE
        # ====================================================

        intelligence = (
            self.intelligence.calculate(
                analysis
            )
        )


        # ====================================================
        # 7. NEXT BEST ACTION
        # ====================================================

        decision = (
            self.decision_engine.decide(

                hcp_profile,

                analysis

            )
        )


        # ====================================================
        # 8. CRITIC
        # ====================================================

        critic_result = (
            self.critic.check(

                hcp_profile,

                analysis,

                decision

            )
        )


        # ====================================================
        # 9. NORMAL EXPLANATION
        # ====================================================

        explanation = (
            self.explainer.generate(

                hcp_profile,

                analysis,

                decision,

                critic_result

            )
        )


        # ====================================================
        # 10. LOCAL AI EXPLANATION
        # ====================================================

        local_ai_explanation = None


        if self.local_ai_available:

            try:

                local_ai_explanation = (
                    self.local_ai.explain(

                        decision=decision,

                        analysis=analysis,

                        critic=critic_result

                    )
                )

            except Exception as error:

                print(
                    "Local AI generation failed:"
                )

                print(error)


        # ====================================================
        # 11. SAVE TO MEMORY
        # ====================================================

        self.memory.save(

            hcp_id,

            objective,

            decision,

            critic_result

        )


        # ====================================================
        # 12. READ MEMORY
        # ====================================================

        previous_decisions = (
            self.memory.get_history(

                hcp_id,

                limit=10

            )
        )


        # ====================================================
        # 13. RETURN COMPLETE RESULT
        # ====================================================

        return {

            "hcp_id":
                hcp_id,

            "objective":
                objective,

            "plan":
                plan,

            "hcp_profile":
                hcp_profile,

            "engagement_history":
                engagement_history,

            "channel_scores":
                channel_scores,

            "analysis":
                analysis,

            "intelligence":
                intelligence,

            "decision":
                decision,

            "critic":
                critic_result,

            "explanation":
                explanation,

            "local_ai_explanation":
                local_ai_explanation,

            "local_ai_enabled":
                self.local_ai_available,

            "memory":
                previous_decisions

        }
