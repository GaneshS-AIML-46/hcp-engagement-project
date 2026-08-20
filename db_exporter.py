"""
Azure PostgreSQL Exporter Script
Connects to Azure Database for PostgreSQL and uploads the exported datasets
(HCP_Entropy_and_ML_Recommendations.csv and HCP_ML_Channel_Recommendations.csv).
"""

import os
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

BASE_DIR = Path(r"c:\Users\GANESH\Desktop\weight")

# Default connection parameters (Replace with your Azure PostgreSQL details)
DB_HOST = os.getenv("AZURE_POSTGRES_HOST", "hcp-student-db.postgres.database.azure.com")
DB_NAME = os.getenv("AZURE_POSTGRES_DB", "postgres")
DB_USER = os.getenv("AZURE_POSTGRES_USER", "pgadmin")
DB_PASSWORD = os.getenv("AZURE_POSTGRES_PASSWORD", "StudentPass2026!")
DB_PORT = os.getenv("AZURE_POSTGRES_PORT", "5432")


def export_to_azure_postgres():
    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    print(f"Connecting to Azure PostgreSQL at {DB_HOST}...")

    engine = create_engine(connection_string)

    entropy_csv = BASE_DIR / "HCP_Entropy_and_ML_Recommendations.csv"
    ml_recs_csv = BASE_DIR / "HCP_ML_Channel_Recommendations.csv"

    if not entropy_csv.exists():
        print(f"Error: {entropy_csv} not found. Run pipeline.py first.")
        return

    print("Uploading HCP Entropy & Engagement Scores table...")
    entropy_df = pd.read_csv(entropy_csv)
    entropy_df.to_sql("hcp_entropy_scores", engine, if_exists="replace", index=False)
    print(f"[SUCCESS] Uploaded {len(entropy_df)} rows to table 'hcp_entropy_scores'.")

    if ml_recs_csv.exists():
        print("Uploading HCP ML Channel Recommendations table...")
        ml_df = pd.read_csv(ml_recs_csv)
        ml_df.to_sql("hcp_ml_recommendations", engine, if_exists="replace", index=False)
        print(f"[SUCCESS] Uploaded {len(ml_df)} rows to table 'hcp_ml_recommendations'.")

    print("\n✅ All datasets successfully stored in Azure PostgreSQL!")


if __name__ == "__main__":
    export_to_azure_postgres()
