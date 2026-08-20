
# ============================================================
# AgentKF - ML PREDICTION ADAPTER
# ============================================================

import pandas as pd


class MLPredictionAdapter:
    """
    Reads ML prediction outputs and converts them
    into AgentKF channel scores.
    """


    def __init__(self, prediction_data):

        self.prediction_data = prediction_data


    def prepare(self):

        if self.prediction_data is None:

            return []


        df = self.prediction_data.copy()


        # Normalize column names

        df.columns = [

            str(column)
            .strip()
            .lower()
            .replace(" ", "_")

            for column
            in df.columns

        ]


        # ----------------------------------------------------
        # HCP ID
        # ----------------------------------------------------

        possible_id_columns = [

            "hcp_id",
            "hcpid",
            "hcp",
            "id"

        ]


        id_column = None


        for column in possible_id_columns:

            if column in df.columns:

                id_column = column
                break


        if id_column is None:

            raise ValueError(
                "ML prediction data does not "
                "contain an HCP ID column."
            )


        if id_column != "hcp_id":

            df = df.rename(

                columns={
                    id_column: "hcp_id"
                }

            )


        df["hcp_id"] = (

            df["hcp_id"]
            .astype(str)

        )


        # ----------------------------------------------------
        # Find probability column
        # ----------------------------------------------------

        possible_probability_columns = [

            "probability",
            "prediction_probability",
            "ensemble_probability",
            "ensemble_score",
            "score",
            "engagement_probability"

        ]


        probability_column = None


        for column in possible_probability_columns:

            if column in df.columns:

                probability_column = column
                break


        if probability_column is None:

            raise ValueError(
                "No ML probability/score column found."
            )


        # ----------------------------------------------------
        # Find channel column
        # ----------------------------------------------------

        possible_channel_columns = [

            "channel",
            "preferred_channel",
            "engagement_channel"

        ]


        channel_column = None


        for column in possible_channel_columns:

            if column in df.columns:

                channel_column = column
                break


        if channel_column is None:

            raise ValueError(
                "No channel column found "
                "in ML prediction data."
            )


        # ----------------------------------------------------
        # Standardize output
        # ----------------------------------------------------

        result = pd.DataFrame({

            "hcp_id":
                df["hcp_id"],

            "channel":
                df[channel_column],

            "probability":
                pd.to_numeric(
                    df[probability_column],
                    errors="coerce"
                )

        })


        # Convert 0-1 probabilities to percentage
        # only when values look like probabilities.

        if (
            not result["probability"].dropna().empty
            and
            result["probability"].dropna().max() <= 1
        ):

            result["probability"] = (
                result["probability"] * 100
            )


        result["probability"] = (
            result["probability"]
            .round(2)
        )


        return result.to_dict(
            orient="records"
        )
