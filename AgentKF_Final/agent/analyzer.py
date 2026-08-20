
# ============================================================
# AgentKF - ANALYSIS ENGINE
# ============================================================


class EngagementAnalyzer:
    """
    Analyzes an HCP's engagement history.
    """


    def analyze(self, engagement_history):

        total_attempts = len(
            engagement_history
        )

        successful_attempts = sum(
            1
            for record in engagement_history
            if record.get("successful") is True
        )

        failed_attempts = (
            total_attempts
            - successful_attempts
        )

        if total_attempts > 0:

            success_rate = (
                successful_attempts
                / total_attempts
            )

        else:

            success_rate = 0


        return {

            "total_attempts":
                total_attempts,

            "successful_attempts":
                successful_attempts,

            "failed_attempts":
                failed_attempts,

            "success_rate":
                round(
                    success_rate,
                    3
                )

        }



class ChannelAnalyzer:
    """
    Analyzes channel predictions.
    """


    def analyze(self, channel_scores):

        if not channel_scores:

            return {

                "best_channel": None,

                "best_probability": 0,

                "channels": []

            }


        # Channel scores are already sorted
        best = channel_scores[0]


        return {

            "best_channel":
                best.get("channel"),

            "best_probability":
                best.get("probability"),

            "channels":
                channel_scores

        }



class FatigueAnalyzer:
    """
    Estimates outreach fatigue.

    Higher score means the HCP may be receiving
    too much or too-frequent outreach.
    """


    def analyze(self, engagement_history):

        total_attempts = len(
            engagement_history
        )


        failed_attempts = sum(

            1

            for record
            in engagement_history

            if record.get("successful") is False

        )


        # Simple demonstration formula
        #
        # More attempts + more failures
        # = higher fatigue.


        attempt_factor = min(
            total_attempts / 10,
            1
        )


        failure_factor = (

            failed_attempts / total_attempts

            if total_attempts > 0

            else 0

        )


        fatigue_score = (

            0.5 * attempt_factor
            +
            0.5 * failure_factor

        ) * 100


        if fatigue_score >= 70:

            band = "HIGH"

        elif fatigue_score >= 40:

            band = "MEDIUM"

        else:

            band = "LOW"


        return {

            "fatigue_score":
                round(
                    fatigue_score,
                    2
                ),

            "fatigue_band":
                band

        }



class TrendAnalyzer:
    """
    Determines whether engagement appears
    to be improving, stable, or declining.
    """


    def analyze(self, engagement_history):

        if len(
            engagement_history
        ) < 2:

            return {

                "trend":
                    "INSUFFICIENT_DATA",

                "trend_score":
                    0

            }


        # Newest record is assumed to be
        # first in our temporary dataset.

        recent = engagement_history[0]

        older = engagement_history[-1]


        recent_success = (

            1
            if recent.get("successful")
            else 0

        )


        older_success = (

            1
            if older.get("successful")
            else 0

        )


        difference = (
            recent_success
            -
            older_success
        )


        if difference > 0:

            trend = "IMPROVING"

        elif difference < 0:

            trend = "DECLINING"

        else:

            trend = "STABLE"


        return {

            "trend":
                trend,

            "trend_score":
                difference

        }



class AnalysisEngine:
    """
    Combines all analysis components.
    """


    def __init__(self):

        self.engagement_analyzer = (
            EngagementAnalyzer()
        )

        self.channel_analyzer = (
            ChannelAnalyzer()
        )

        self.fatigue_analyzer = (
            FatigueAnalyzer()
        )

        self.trend_analyzer = (
            TrendAnalyzer()
        )


    def analyze(
        self,
        engagement_history,
        channel_scores
    ):

        engagement = (
            self.engagement_analyzer.analyze(
                engagement_history
            )
        )


        channels = (
            self.channel_analyzer.analyze(
                channel_scores
            )
        )


        fatigue = (
            self.fatigue_analyzer.analyze(
                engagement_history
            )
        )


        trend = (
            self.trend_analyzer.analyze(
                engagement_history
            )
        )


        return {

            "engagement": engagement,

            "channels": channels,

            "fatigue": fatigue,

            "trend": trend

        }
