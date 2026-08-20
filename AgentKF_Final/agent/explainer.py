
# ============================================================
# AgentKF - EXPLANATION GENERATOR
# ============================================================


class ExplanationGenerator:
    """
    Converts the Agent's technical decision
    into a simple human-readable explanation.
    """


    def generate(
        self,
        hcp_profile,
        analysis,
        decision,
        critic
    ):

        action = decision.get(
            "action"
        )

        channel = decision.get(
            "channel"
        )

        priority = decision.get(
            "priority"
        )

        reason = decision.get(
            "reason"
        )


        best_probability = (
            analysis
            .get("channels", {})
            .get("best_probability", 0)
        )


        fatigue = (
            analysis
            .get("fatigue", {})
            .get("fatigue_band", "UNKNOWN")
        )


        trend = (
            analysis
            .get("trend", {})
            .get("trend", "UNKNOWN")
        )


        # ----------------------------------------------------
        # Main explanation
        # ----------------------------------------------------

        if action == "TARGETED_ENGAGEMENT":

            summary = (

                f"The Agent recommends "
                f"TARGETED ENGAGEMENT through "
                f"{channel}. "

                f"The predicted engagement "
                f"probability is "
                f"{best_probability}%. "

                f"The current fatigue level is "
                f"{fatigue}, and the engagement "
                f"trend is {trend}."

            )


        elif action == "RE_ENGAGE":

            summary = (

                f"The Agent recommends "
                f"RE-ENGAGEMENT through "
                f"{channel}. "

                f"Recent engagement appears to "
                f"be declining, so a focused "
                f"re-engagement strategy is recommended."

            )


        elif action == "COOL_DOWN":

            summary = (

                "The Agent recommends a COOL-DOWN "
                "period because the HCP shows "
                "high outreach fatigue."

            )


        elif action == "DO_NOT_CONTACT":

            summary = (

                "The Agent recommends DO NOT CONTACT "
                "because communication should not "
                "be attempted for this HCP."

            )


        else:

            summary = (

                "The Agent recommends MANUAL REVIEW "
                "because there is not enough confidence "
                "for an automatic engagement decision."

            )


        return {

            "summary":
                summary,

            "technical_reason":
                reason,

            "priority":
                priority,

            "critic_status":
                critic.get("status"),

            "warnings":
                critic.get("warnings", []),

            "next_step":
                action

        }
