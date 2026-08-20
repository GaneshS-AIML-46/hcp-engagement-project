
# ============================================================
# AgentKF - FREE LOCAL AI
# Direct FLAN-T5 Implementation
# ============================================================

import torch


class LocalAI:

    def __init__(
        self,
        model_name="google/flan-t5-small"
    ):

        self.model_name = model_name

        self.tokenizer = None

        self.model = None

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.loaded = False


    # ========================================================
    # LOAD MODEL
    # ========================================================

    def load(self):

        try:

            from transformers import (
                AutoTokenizer,
                AutoModelForSeq2SeqLM
            )

            print(
                "Loading local model:",
                self.model_name
            )

            print(
                "Device:",
                self.device
            )


            # ------------------------------------------------
            # Load tokenizer
            # ------------------------------------------------

            self.tokenizer = (
                AutoTokenizer.from_pretrained(
                    self.model_name
                )
            )


            # ------------------------------------------------
            # Load FLAN-T5 model
            # ------------------------------------------------

            self.model = (
                AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_name
                )
            )


            # ------------------------------------------------
            # Move model to CPU/GPU
            # ------------------------------------------------

            self.model = self.model.to(
                self.device
            )


            self.model.eval()


            self.loaded = True


            print()
            print(
                "✅ Local FLAN-T5 model loaded successfully."
            )

            return True


        except Exception as error:

            print()
            print(
                "❌ Local AI could not be loaded."
            )

            print(
                "Reason:",
                error
            )

            self.loaded = False

            return False


    # ========================================================
    # GENERATE EXPLANATION
    # ========================================================

    def explain(
        self,
        decision,
        analysis,
        critic
    ):

        if not self.loaded:

            return None


        action = decision.get(
            "action",
            "UNKNOWN"
        )


        channel = decision.get(
            "channel",
            "UNKNOWN"
        )


        priority = decision.get(
            "priority",
            "UNKNOWN"
        )


        reason = decision.get(
            "reason",
            "No reason available."
        )


        probability = (

            analysis
            .get("channels", {})
            .get(
                "best_probability",
                0
            )

        )


        fatigue = (

            analysis
            .get("fatigue", {})
            .get(
                "fatigue_band",
                "UNKNOWN"
            )

        )


        trend = (

            analysis
            .get("trend", {})
            .get(
                "trend",
                "UNKNOWN"
            )

        )


        critic_status = critic.get(
            "status",
            "UNKNOWN"
        )


        # ----------------------------------------------------
        # Prompt
        # ----------------------------------------------------

        prompt = f"""
Explain this HCP engagement recommendation
in simple professional language.

Action: {action}

Channel: {channel}

Priority: {priority}

Predicted probability: {probability}

Fatigue level: {fatigue}

Engagement trend: {trend}

Critic status: {critic_status}

Reason: {reason}

Use only the information provided.
Do not invent facts.
Keep the explanation short.
"""


        try:

            # ------------------------------------------------
            # Tokenize
            # ------------------------------------------------

            inputs = self.tokenizer(

                prompt,

                return_tensors="pt",

                truncation=True,

                max_length=512

            )


            # ------------------------------------------------
            # Move inputs to same device
            # ------------------------------------------------

            inputs = {

                key: value.to(
                    self.device
                )

                for key, value
                in inputs.items()

            }


            # ------------------------------------------------
            # Generate
            # ------------------------------------------------

            with torch.no_grad():

                outputs = (
                    self.model.generate(

                        **inputs,

                        max_new_tokens=100,

                        do_sample=False

                    )
                )


            # ------------------------------------------------
            # Decode
            # ------------------------------------------------

            explanation = (
                self.tokenizer.decode(

                    outputs[0],

                    skip_special_tokens=True

                )
            )


            return explanation


        except Exception as error:

            print()
            print(
                "❌ Local AI generation failed:"
            )

            print(error)

            return None


    # ========================================================
    # SIMPLE TEST
    # ========================================================

    def test(self):

        if not self.loaded:

            return False


        test_decision = {

            "action":
                "TARGETED_ENGAGEMENT",

            "channel":
                "Email",

            "priority":
                "HIGH",

            "reason":
                "Email has the highest predicted "
                "engagement probability."

        }


        test_analysis = {

            "channels": {

                "best_probability":
                    82

            },

            "fatigue": {

                "fatigue_band":
                    "LOW"

            },

            "trend": {

                "trend":
                    "STABLE"

            }

        }


        test_critic = {

            "status":
                "PASSED"

        }


        result = self.explain(

            decision=test_decision,

            analysis=test_analysis,

            critic=test_critic

        )


        print()
        print(
            "======================================"
        )

        print(
            "       LOCAL AI TEST RESULT"
        )

        print(
            "======================================"
        )

        print()

        print(result)

        return result is not None
