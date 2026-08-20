
# ============================================================
# AgentKF - DECISION INTELLIGENCE
# ============================================================


class DecisionIntelligence:

    """
    Combines ML prediction and behavioral signals
    to help the Agent prioritize its recommendation.
    """


    def calculate(
        self,
        analysis
    ):

        channels = (
            analysis
            .get("channels", {})
            .get("channels", [])
        )


        engagement = (
            analysis
            .get("engagement", {})
        )


        fatigue = (
            analysis
            .get("fatigue", {})
        )


        trend = (
            analysis
            .get("trend", {})
        )


        historical_success = (
            float(
                engagement.get(
                    "success_rate",
                    0
                )
            )
            * 100
        )


        fatigue_score = float(
            fatigue.get(
                "fatigue_score",
                0
            )
        )


        trend_name = trend.get(
            "trend",
            "UNKNOWN"
        )


        # ----------------------------------------------------
        # Trend adjustment
        # ----------------------------------------------------

        if trend_name == "IMPROVING":

            trend_adjustment = 10

        elif trend_name == "DECLINING":

            trend_adjustment = -10

        else:

            trend_adjustment = 0


        ranked = []


        for channel in channels:

            probability = float(
                channel.get(
                    "probability",
                    0
                )
            )


            # Base ML probability
            ml_component = (
                probability * 0.60
            )


            # Historical engagement
            history_component = (
                historical_success * 0.20
            )


            # Fatigue penalty
            fatigue_penalty = (
                fatigue_score * 0.15
            )


            # Trend
            trend_component = (
                trend_adjustment * 0.05
            )


            intelligence_score = (

                ml_component

                + history_component

                + trend_component

                - fatigue_penalty

            )


            # Keep score within 0-100
            intelligence_score = max(
                0,
                min(
                    100,
                    intelligence_score
                )
            )


            ranked.append({

                "channel":
                    channel.get("channel"),

                "ml_probability":
                    probability,

                "historical_success_rate":
                    round(
                        historical_success,
                        2
                    ),

                "fatigue_score":
                    round(
                        fatigue_score,
                        2
                    ),

                "trend":
                    trend_name,

                "intelligence_score":
                    round(
                        intelligence_score,
                        2
                    )

            })


        ranked.sort(

            key=lambda x:
                x["intelligence_score"],

            reverse=True

        )


        return ranked
