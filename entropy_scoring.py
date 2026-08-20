"""
Entropy Engagement Scoring Module
Strictly calculates dynamic Shannon Entropy engagement scores (component weights + channel weights)
without using any arbitrary weight assignments.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def entropy_weights(data: pd.DataFrame) -> pd.DataFrame:
    """
    EIML Shannon Entropy-weight method; returns entropy, diversification, and normalized weights.
    """
    X = data.astype(float).fillna(0).clip(lower=0)
    epsilon = 1e-12
    column_sums = X.sum(axis=0)
    P = X.div(column_sums.replace(0, epsilon), axis=1)
    n = len(X)
    if n <= 1:
        raise ValueError("Entropy calculation requires more than one observation.")
    k = 1 / np.log(n)
    entropy = -k * (P * np.log(P + epsilon)).sum(axis=0)
    diversification = (1 - entropy).clip(lower=0)
    weights = diversification / diversification.sum()
    if weights.isna().any() or np.isclose(weights.sum(), 0):
        weights = pd.Series(1 / len(diversification), index=diversification.index)
    return pd.DataFrame({"entropy": entropy, "diversification": diversification, "weight": weights})


def calculate_entropy_scores(
    hcp_df: pd.DataFrame,
    engagement_df: pd.DataFrame,
    channels=None
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Computes Entropy Engagement Scores for HCPs.
    Returns (final_dataset, component_weights_df, channel_weights_df).
    """
    if channels is None:
        channels = ["rep_visit", "phone_call", "webinar", "email", "digital_ad"]

    # Copy data
    engagement_df = engagement_df.copy()
    if "engagement_date" in engagement_df.columns:
        engagement_df["engagement_date"] = pd.to_datetime(engagement_df["engagement_date"])

    reference_date = engagement_df["engagement_date"].max()

    # Aggregate engagement by HCP x channel
    engagement_summary = (
        engagement_df.groupby(["hcp_id", "channel"], as_index=False)
        .agg(
            interaction_count=("engagement_successful", "size"),
            success_rate=("engagement_successful", "mean"),
            last_engagement_date=("engagement_date", "max"),
        )
    )
    engagement_summary["recency_days"] = (
        reference_date - engagement_summary["last_engagement_date"]
    ).dt.days

    # Pivot metrics to HCP level
    channel_features = engagement_summary.pivot(
        index="hcp_id",
        columns="channel",
        values=["interaction_count", "success_rate", "recency_days"],
    )
    channel_features.columns = [f"{metric}_{channel}" for metric, channel in channel_features.columns]
    channel_features = channel_features.reset_index()

    # Ensure all channels & metrics exist
    for channel in channels:
        for metric in ["interaction_count", "success_rate"]:
            column = f"{metric}_{channel}"
            if column not in channel_features.columns:
                channel_features[column] = 0.0
            channel_features[column] = pd.to_numeric(channel_features[column], errors="coerce").fillna(0.0)
        recency_column = f"recency_days_{channel}"
        if recency_column not in channel_features.columns:
            channel_features[recency_column] = np.nan

    # Calculate component scores (Frequency, Recency, Success Rate)
    for channel in channels:
        count_col = f"interaction_count_{channel}"
        max_count = channel_features[count_col].max()
        channel_features[f"frequency_score_{channel}"] = (
            channel_features[count_col] / max_count if max_count > 0 else 0.0
        )

        recency = channel_features[f"recency_days_{channel}"].fillna(9999).astype(float)
        channel_features[f"recency_score_{channel}"] = np.where(
            channel_features[count_col] > 0,
            1 / (1 + recency / 30),
            0.0,
        )
        channel_features[f"success_score_{channel}"] = channel_features[f"success_rate_{channel}"].clip(0, 1)

    # First entropy calculation: Component weights (frequency, success_rate, recency)
    indicator_data = pd.DataFrame({
        "frequency": np.concatenate([channel_features[f"frequency_score_{c}"].to_numpy() for c in channels]),
        "success_rate": np.concatenate([channel_features[f"success_score_{c}"].to_numpy() for c in channels]),
        "recency": np.concatenate([channel_features[f"recency_score_{c}"].to_numpy() for c in channels]),
    })
    indicator_weights = entropy_weights(indicator_data)

    w_frequency = indicator_weights.loc["frequency", "weight"]
    w_success = indicator_weights.loc["success_rate", "weight"]
    w_recency = indicator_weights.loc["recency", "weight"]

    for channel in channels:
        channel_features[f"entropy_channel_score_{channel}"] = (
            w_frequency * channel_features[f"frequency_score_{channel}"]
            + w_success * channel_features[f"success_score_{channel}"]
            + w_recency * channel_features[f"recency_score_{channel}"]
        )

    # Second entropy calculation: Channel weights
    entropy_score_cols = [f"entropy_channel_score_{channel}" for channel in channels]
    channel_score_data = channel_features[entropy_score_cols].copy()
    channel_score_data.columns = channels
    channel_weights = entropy_weights(channel_score_data)

    # Overall Entropy Engagement Score (0 - 100)
    channel_features["entropy_weighted_score"] = 100 * sum(
        channel_features[f"entropy_channel_score_{channel}"] * channel_weights.loc[channel, "weight"]
        for channel in channels
    )
    channel_features["entropy_weighted_score"] = channel_features["entropy_weighted_score"].round(2)
    channel_features["entropy_weighted_rank"] = (
        channel_features["entropy_weighted_score"].rank(method="min", ascending=False).astype(int)
    )

    # Determine recommended channel
    channel_features["recommended_channel"] = (
        channel_features[entropy_score_cols].idxmax(axis=1).str.replace("entropy_channel_score_", "", regex=False)
    )
    channel_features.loc[channel_features[entropy_score_cols].sum(axis=1).eq(0), "recommended_channel"] = "No engagement history"

    # Merge back to HCP Master
    final_dataset = hcp_df.merge(channel_features, on="hcp_id", how="left", validate="one_to_one")
    if "opt_out_flag" in final_dataset.columns:
        final_dataset["engagement_eligible"] = ~final_dataset["opt_out_flag"].fillna(False)
        final_dataset.loc[~final_dataset["engagement_eligible"], "recommended_channel"] = "Do Not Contact"

    return final_dataset, indicator_weights, channel_weights


if __name__ == "__main__":
    base_dir = Path(r"c:\Users\GANESH\Desktop\weight")
    hcp_df = pd.read_csv(base_dir / "HCP_master_updated.csv")
    engagement_df = pd.read_csv(base_dir / "Engagement_history_improved.csv")
    df, ind_w, ch_w = calculate_entropy_scores(hcp_df, engagement_df)
    print("Entropy scoring completed!")
    print(f"Top 5 HCP scores:\n{df[['hcp_id', 'entropy_weighted_score', 'entropy_weighted_rank', 'recommended_channel']].head()}")
