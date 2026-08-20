
# ============================================================
# AgentKF - CRITIC / GUARDRAILS
# ============================================================


class AgentCritic:
    """
    Checks whether the Agent's proposed decision
    is valid and safe.
    """

    def check(
        self,
        hcp_profile,
        analysis,
        decision
    ):

        warnings = []
        errors = []

        # ----------------------------------------------------
        # CHECK 1 — HCP PROFILE
        # ----------------------------------------------------

        if hcp_profile is None:

            errors.append(
                "HCP profile was not found."
            )


        # ----------------------------------------------------
        # CHECK 2 — OPT-OUT
        # ----------------------------------------------------

        opt_out = hcp_profile.get(
            "opt_out",
            False
        ) if hcp_profile else False


        if opt_out is True:

            errors.append(
                "HCP has opted out of communication."
            )


        # ----------------------------------------------------
        # CHECK 3 — CHANNEL
        # ----------------------------------------------------

        best_channel = (
            analysis
            .get("channels", {})
            .get("best_channel")
        )


        if (
            decision.get("action")
            == "TARGETED_ENGAGEMENT"
            and best_channel is None
        ):

            errors.append(
                "Agent recommended engagement "
                "without a valid channel."
            )


        # ----------------------------------------------------
        # CHECK 4 — FATIGUE
        # ----------------------------------------------------

        fatigue_band = (
            analysis
            .get("fatigue", {})
            .get("fatigue_band", "LOW")
        )


        if (
            fatigue_band == "HIGH"
            and decision.get("action")
            == "TARGETED_ENGAGEMENT"
        ):

            warnings.append(
                "High fatigue detected. "
                "Consider cooling down outreach."
            )


        # ----------------------------------------------------
        # CHECK 5 — PROBABILITY
        # ----------------------------------------------------

        probability = (
            analysis
            .get("channels", {})
            .get("best_probability", 0)
        )


        try:
            probability = float(probability)
        except:
            probability = 0


        if (
            decision.get("action")
            == "TARGETED_ENGAGEMENT"
            and probability < 50
        ):

            warnings.append(
                "Recommended channel has "
                "low predicted engagement probability."
            )


        # ----------------------------------------------------
        # FINAL STATUS
        # ----------------------------------------------------

        if errors:

            status = "BLOCKED"

        elif warnings:

            status = "WARNING"

        else:

            status = "PASSED"


        return {

            "status":
                status,

            "passed":
                len(errors) == 0,

            "warnings":
                warnings,

            "errors":
                errors,

            "checks_performed": [

                "HCP profile validation",

                "Opt-out validation",

                "Channel validation",

                "Fatigue validation",

                "Prediction probability validation"

            ]

        }
