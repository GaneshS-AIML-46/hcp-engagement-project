"""
ML Model Training and Serialization Script
Trains leakage-safe Calibrated Random Forest Classifier for HCP Channel Recommendation
and exports the model to a .pkl pickle file for local & Azure hosting.
"""

import os
import pickle
import joblib
from pathlib import Path
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV


CHANNELS = ["email", "webinar", "rep_visit", "digital_ad", "phone_call"]


def build_historical_features(hcp_df: pd.DataFrame, history_df: pd.DataFrame):
    """
    Builds leakage-safe training features for each historical engagement record (optimized O(N)).
    """
    history = history_df.loc[history_df["channel"].isin(CHANNELS)].copy()
    history["target"] = history["engagement_successful"].astype(int)
    history["engagement_date"] = pd.to_datetime(history["engagement_date"])
    history = history.sort_values(["engagement_date", "hcp_id"]).reset_index(drop=True)

    feature_rows = []
    
    # Process sequentially by HCP for maximum performance
    for hcp_id, group in history.groupby("hcp_id", sort=False):
        channel_counts = {c: 0 for c in CHANNELS}
        channel_successes = {c: 0 for c in CHANNELS}
        channel_last_dates = {c: None for c in CHANNELS}

        for _, event in group.iterrows():
            evt_date = event["engagement_date"]
            evt_channel = event["channel"]

            row = {
                "hcp_id": hcp_id,
                "prediction_date": evt_date,
                "candidate_channel": evt_channel,
                "target": event["target"],
            }

            active_channels = 0
            for c in CHANNELS:
                cnt = channel_counts[c]
                row[f"{c}_freq"] = cnt
                row[f"{c}_success_rate"] = (channel_successes[c] / cnt) if cnt > 0 else 0.0
                row[f"{c}_recency_days"] = (evt_date - channel_last_dates[c]).days if channel_last_dates[c] is not None else np.nan
                row[f"{c}_has_history"] = int(cnt > 0)
                if cnt > 0:
                    active_channels += 1

            row["channel_diversity"] = active_channels
            feature_rows.append(row)

            # Update state AFTER capturing historical state (leakage-safe)
            channel_counts[evt_channel] += 1
            channel_successes[evt_channel] += event["target"]
            channel_last_dates[evt_channel] = evt_date

    ml_df = pd.DataFrame(feature_rows)

    # Merge HCP attributes
    attribute_candidates = ["specialty", "segment", "territory", "practice_type", "account_tenure", "opt_out_flag", "channel_preference"]
    attribute_columns = [col for col in attribute_candidates if col in hcp_df.columns]
    hcp_features = hcp_df[["hcp_id"] + attribute_columns].drop_duplicates("hcp_id")
    ml_df = ml_df.merge(hcp_features, on="hcp_id", how="left", validate="many_to_one")

    return ml_df


def train_and_export(base_dir: Path):
    """
    Trains the calibrated ML model and exports to models/hcp_channel_ml_model.pkl
    """
    hcp_df = pd.read_csv(base_dir / "HCP_master_updated.csv")
    history_df = pd.read_csv(base_dir / "Engagement_history_improved.csv")

    print("Building historical feature matrix...")
    ml_df = build_historical_features(hcp_df, history_df)

    ml_df = ml_df.sort_values("prediction_date").reset_index(drop=True)
    train_end = int(len(ml_df) * 0.85)
    ml_df["split"] = "test"
    ml_df.loc[:train_end - 1, "split"] = "train"

    exclude_columns = ["target", "hcp_id", "prediction_date", "split"]
    feature_columns = [column for column in ml_df.columns if column not in exclude_columns]
    X_all = pd.get_dummies(ml_df[feature_columns], dummy_na=True).replace([np.inf, -np.inf], np.nan)
    y_all = ml_df["target"].astype(int)

    train_mask = ml_df["split"].eq("train")
    X_train, y_train = X_all.loc[train_mask], y_all.loc[train_mask]

    print("Fitting Random Forest Pipeline...")
    rf_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(
            n_estimators=400,
            min_samples_leaf=3,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=42
        ))
    ])

    print("Fitting CalibratedClassifierCV...")
    calibrated_model = CalibratedClassifierCV(estimator=rf_pipeline, method="sigmoid", cv=3)
    calibrated_model.fit(X_train, y_train)

    # Output directory
    models_dir = base_dir / "models"
    os.makedirs(models_dir, exist_ok=True)

    model_path = models_dir / "hcp_channel_ml_model.pkl"
    metadata_path = models_dir / "model_metadata.pkl"

    metadata = {
        "feature_columns": feature_columns,
        "train_columns": list(X_train.columns),
        "channels": CHANNELS,
        "model_type": "CalibratedClassifierCV(RandomForestClassifier)",
    }

    # Save model and metadata using joblib & pickle
    joblib.dump(calibrated_model, model_path)
    with open(metadata_path, "wb") as f:
        pickle.dump(metadata, f)

    print(f"[SUCCESS] ML Model successfully trained and saved to: {model_path}")
    print(f"[SUCCESS] Model metadata saved to: {metadata_path}")

    return calibrated_model, metadata


def predict_recommendations(calibrated_model, metadata, hcp_df: pd.DataFrame, history_df: pd.DataFrame):
    """
    Generates channel success probabilities and recommendation tiers for all HCPs.
    """
    feature_columns = metadata["feature_columns"]
    train_columns = metadata["train_columns"]

    history = history_df.loc[history_df["channel"].isin(CHANNELS)].copy()
    history["target"] = history["engagement_successful"].astype(int)
    history["engagement_date"] = pd.to_datetime(history["engagement_date"])

    scoring_date = history["engagement_date"].max() + pd.Timedelta(days=1)

    attribute_candidates = ["specialty", "segment", "territory", "practice_type", "account_tenure", "opt_out_flag", "channel_preference"]
    attribute_columns = [col for col in attribute_candidates if col in hcp_df.columns]
    hcp_features = hcp_df[["hcp_id"] + attribute_columns].drop_duplicates("hcp_id")

    candidate_rows = []
    for hcp_id, group in history.groupby("hcp_id", sort=False):
        for candidate_channel in CHANNELS:
            row = {
                "hcp_id": hcp_id,
                "prediction_date": scoring_date,
                "candidate_channel": candidate_channel,
            }
            active_channels = 0
            for channel in CHANNELS:
                channel_history = group.loc[group["channel"].eq(channel)]
                frequency = len(channel_history)
                row[f"{channel}_freq"] = frequency
                row[f"{channel}_success_rate"] = channel_history["target"].mean() if frequency else 0.0
                row[f"{channel}_recency_days"] = (
                    (scoring_date - channel_history["engagement_date"].max()).days if frequency else np.nan
                )
                row[f"{channel}_has_history"] = int(frequency > 0)
                if frequency > 0:
                    active_channels += 1
            row["channel_diversity"] = active_channels
            candidate_rows.append(row)

    # Ensure HCPs with zero history are also included
    existing_hcps = set(history["hcp_id"].unique())
    all_hcps = set(hcp_df["hcp_id"].unique())
    missing_hcps = all_hcps - existing_hcps

    for hcp_id in missing_hcps:
        for candidate_channel in CHANNELS:
            row = {
                "hcp_id": hcp_id,
                "prediction_date": scoring_date,
                "candidate_channel": candidate_channel,
            }
            for channel in CHANNELS:
                row[f"{channel}_freq"] = 0
                row[f"{channel}_success_rate"] = 0.0
                row[f"{channel}_recency_days"] = np.nan
                row[f"{channel}_has_history"] = 0
            row["channel_diversity"] = 0
            candidate_rows.append(row)

    candidate_features = pd.DataFrame(candidate_rows).merge(hcp_features, on="hcp_id", how="left")
    candidate_X = (
        pd.get_dummies(candidate_features[feature_columns], dummy_na=True)
        .reindex(columns=train_columns, fill_value=0)
        .replace([np.inf, -np.inf], np.nan)
    )

    probs = calibrated_model.predict_proba(candidate_X)[:, 1]
    candidate_features["success_probability"] = probs.round(4)

    # Assign recommendation tiers per HCP
    candidate_features = candidate_features.sort_values(["hcp_id", "success_probability"], ascending=[True, False]).reset_index(drop=True)

    tier_map = {0: "Primary", 1: "Secondary", 2: "Supporting"}
    candidate_features["rank_in_hcp"] = candidate_features.groupby("hcp_id").cumcount()
    candidate_features["recommendation_tier"] = candidate_features["rank_in_hcp"].map(tier_map).fillna("Other")

    return candidate_features


if __name__ == "__main__":
    base_dir = Path(r"c:\Users\GANESH\Desktop\weight")
    model, meta = train_and_export(base_dir)
    hcp_df = pd.read_csv(base_dir / "HCP_master_updated.csv")
    history_df = pd.read_csv(base_dir / "Engagement_history_improved.csv")
    recs = predict_recommendations(model, meta, hcp_df, history_df)
    print(f"Generated {len(recs)} candidate channel recommendations!")
    print(recs[["hcp_id", "candidate_channel", "success_probability", "recommendation_tier"]].head(10))
