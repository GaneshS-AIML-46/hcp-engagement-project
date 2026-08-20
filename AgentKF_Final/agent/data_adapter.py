
# ============================================================
# AgentKF - REAL DATA ADAPTER
# ============================================================

import pandas as pd


class AgentDataAdapter:
    """
    Converts project datasets into the format expected
    by AgentKF.

    This allows AgentKF to work with datasets created
    by other parts of the project.
    """

    def __init__(
        self,
        hcp_data=None,
        engagement_data=None,
        channel_data=None
    ):

        self.hcp_data = hcp_data
        self.engagement_data = engagement_data
        self.channel_data = channel_data


    # ========================================================
    # HCP DATA
    # ========================================================

    def prepare_hcp_data(self):

        if self.hcp_data is None:
            return []

        df = self.hcp_data.copy()

        # Convert column names to lowercase
        df.columns = [
            str(c).strip().lower()
            for c in df.columns
        ]

        # Find possible HCP ID column
        possible_ids = [
            "hcp_id",
            "hcpid",
            "hcp",
            "id"
        ]

        id_column = None

        for column in possible_ids:

            if column in df.columns:
                id_column = column
                break

        if id_column is None:

            raise ValueError(
                "No HCP ID column found."
            )

        # Standardize ID name
        if id_column != "hcp_id":

            df = df.rename(
                columns={
                    id_column: "hcp_id"
                }
            )

        # Convert IDs to strings
        df["hcp_id"] = (
            df["hcp_id"]
            .astype(str)
        )

        return df.to_dict(
            orient="records"
        )


    # ========================================================
    # ENGAGEMENT DATA
    # ========================================================

    def prepare_engagement_data(self):

        if self.engagement_data is None:
            return []

        df = self.engagement_data.copy()

        df.columns = [
            str(c).strip().lower()
            for c in df.columns
        ]

        possible_ids = [
            "hcp_id",
            "hcpid",
            "hcp",
            "id"
        ]

        id_column = None

        for column in possible_ids:

            if column in df.columns:
                id_column = column
                break

        if id_column is None:

            raise ValueError(
                "No HCP ID column found "
                "in engagement data."
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

        return df.to_dict(
            orient="records"
        )


    # ========================================================
    # CHANNEL DATA
    # ========================================================

    def prepare_channel_data(self):

        if self.channel_data is None:
            return []

        df = self.channel_data.copy()

        df.columns = [
            str(c).strip().lower()
            for c in df.columns
        ]

        possible_ids = [
            "hcp_id",
            "hcpid",
            "hcp",
            "id"
        ]

        id_column = None

        for column in possible_ids:

            if column in df.columns:
                id_column = column
                break

        if id_column is None:

            raise ValueError(
                "No HCP ID column found "
                "in channel data."
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

        return df.to_dict(
            orient="records"
        )


    # ========================================================
    # PREPARE EVERYTHING
    # ========================================================

    def prepare_all(self):

        return {

            "hcp_data":
                self.prepare_hcp_data(),

            "engagement_data":
                self.prepare_engagement_data(),

            "channel_data":
                self.prepare_channel_data()

        }
