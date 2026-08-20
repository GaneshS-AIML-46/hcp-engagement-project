
# ============================================================
# AgentKF - NEXT BEST ACTION ENGINE
# ============================================================


class NextBestActionEngine:
    """
    Converts the Agent's analysis into a recommended action.
    """


    def decide(
        self,
        hcp_profile,
        analysis
    ):

        # ----------------------------------------------------
        # Get information from analysis
        # ----------------------------------------------------

        channels = analysis.get(
            "channels",
            {}
        )

        fatigue = analysis.get(
            "fatigue",
            {}
        )

        trend = analysis.get(
            "trend",
            {}
        )


        # ----------------------------------------------------
        # Get best channel
        # ----------------------------------------------------

        best_channel = channels.get(
            "best_channel"
        )

        best_probability = channels.get(
            "best_probability",
            0
        )


        # ----------------------------------------------------
        # Get fatigue
        # ----------------------------------------------------

        fatigue_band = fatigue.get(
            "fatigue_band",
            "LOW"
        )


        # ----------------------------------------------------
        # Get engagement trend
        # ----------------------------------------------------

        engagement_trend = trend.get(
            "trend",
            "UNKNOWN"
        )


        # ====================================================
        # DECISION RULE 1
        # OPT-OUT
        # ====================================================

        opt_out = hcp_profile.get(
            "opt_out",
            False
        )


        if opt_out is True:

            return {

                "action":
                    "DO_NOT_CONTACT",

                "channel":
                    None,

                "priority":
                    "BLOCKED",

                "reason":
                    "The HCP has opted out of communication."

            }


        # ====================================================
        # DECISION RULE 2
        # HIGH FATIGUE
        # ====================================================

        if fatigue_band == "HIGH":

            return {

                "action":
                    "COOL_DOWN",

                "channel":
                    None,

                "priority":
                    "HIGH",

                "reason":
                    "The HCP shows high outreach fatigue. "
                    "Reduce communication frequency before "
                    "attempting another engagement."

            }


        # ====================================================
        # DECISION RULE 3
        # DECLINING ENGAGEMENT
        # ====================================================

        if engagement_trend == "DECLINING":

            return {

                "action":
                    "RE_ENGAGE",

                "channel":
                    best_channel,

                "priority":
                    "HIGH",

                "reason":
                    "Recent engagement appears to be declining. "
                    "A re-engagement strategy is recommended."

            }


        # ====================================================
        # DECISION RULE 4
        # NO CHANNEL AVAILABLE
        # ====================================================

        if best_channel is None:

            return {

                "action":
                    "MANUAL_REVIEW",

                "channel":
                    None,

                "priority":
                    "MEDIUM",

                "reason":
                    "No channel prediction is available. "
                    "Manual review is required."

            }


        # ====================================================
        # DECISION RULE 5
        # LOW CONFIDENCE
        # ====================================================

        if float(best_probability) < 50:

            return {

                "action":
                    "MANUAL_REVIEW",

                "channel":
                    best_channel,

                "priority":
                    "MEDIUM",

                "reason":
                    "The best predicted channel has relatively "
                    "low engagement probability."

            }


        # ====================================================
        # DECISION RULE 6
        # NORMAL TARGETED ENGAGEMENT
        # ====================================================

        return {

            "action":
                "TARGETED_ENGAGEMENT",

            "channel":
                best_channel,

            "priority":
                (
                    "HIGH"
                    if float(best_probability) >= 70
                    else "MEDIUM"
                ),

            "reason":
                (
                    "The selected channel has the highest "
                    "predicted engagement probability among "
                    "available channels."
                )

        }
