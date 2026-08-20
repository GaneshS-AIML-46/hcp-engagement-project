"""
Master End-to-End Pipeline
Executes Entropy Engagement Scoring & ML Pickle Recommendation generation,
creating the unified HCP dataset with zero arbitrary scoring assumptions.
"""

import sys
from pathlib import Path
import pandas as pd

# Add current directory to path
BASE_DIR = Path(r"c:\Users\GANESH\Desktop\weight")
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from entropy_scoring import calculate_entropy_scores
from train_and_export_model import train_and_export, predict_recommendations


def run_pipeline():
    print("=" * 70)
    print("STARTING OMNICHANNEL SCORING & ML PIPELINE")
    print("=" * 70)

    # 1. Load Raw Datasets
    hcp_file = BASE_DIR / "HCP_master_updated.csv"
    engagement_file = BASE_DIR / "Engagement_history_improved.csv"

    print(f"Reading inputs from:\n  - {hcp_file}\n  - {engagement_file}")
    hcp_df = pd.read_csv(hcp_file)
    engagement_df = pd.read_csv(engagement_file)

    # 2. Execute Entropy Weight Model
    print("\n--- STEP 1: ENTROPY SCORING (NO ARBITRARY WEIGHTS) ---")
    entropy_df, indicator_weights, channel_weights = calculate_entropy_scores(hcp_df, engagement_df)
    print("Component Weights (Entropy):")
    print(indicator_weights[["weight"]])
    print("Channel Weights (Entropy):")
    print(channel_weights[["weight"]])

    # 3. Train & Export ML Pickle Model
    print("\n--- STEP 2: ML MODEL TRAINING & PICKLE EXPORT FOR AZURE ---")
    calibrated_model, metadata = train_and_export(BASE_DIR)

    # 4. Predict Channel Recommendations using ML Pickle Model
    print("\n--- STEP 3: ML CHANNEL PREDICTION INFERENCE ---")
    recommendations_df = predict_recommendations(calibrated_model, metadata, hcp_df, engagement_df)

    # 5. Merge ML Recommendations into Entropy Dataset
    print("\n--- STEP 4: UNIFYING DATASETS ---")
    # Extract top ML recommended channel per HCP
    top_ml_recs = (
        recommendations_df.loc[recommendations_df["recommendation_tier"].eq("Primary")]
        .drop_duplicates("hcp_id")
        [["hcp_id", "candidate_channel", "success_probability"]]
        .rename(columns={
            "candidate_channel": "ml_primary_channel",
            "success_probability": "ml_primary_probability"
        })
    )

    unified_df = entropy_df.merge(top_ml_recs, on="hcp_id", how="left")

    output_csv = BASE_DIR / "HCP_Entropy_and_ML_Recommendations.csv"
    unified_df.to_csv(output_csv, index=False)
    recommendations_df.to_csv(BASE_DIR / "HCP_ML_Channel_Recommendations.csv", index=False)

    print("\n[SUCCESS] PIPELINE COMPLETED!")
    print(f"Unified dataset exported to: {output_csv}")
    print(f"Total HCPs processed: {len(unified_df)}")
    print(f"Average Entropy Score: {unified_df['entropy_weighted_score'].mean():.2f}")
    print(f"Score Range: {unified_df['entropy_weighted_score'].min()} - {unified_df['entropy_weighted_score'].max()}")
    print("=" * 70)

    return unified_df, recommendations_df


if __name__ == "__main__":
    run_pipeline()
