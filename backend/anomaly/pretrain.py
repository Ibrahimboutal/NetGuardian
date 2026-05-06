import pandas as pd
import numpy as np
import logging
import pickle
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAGGLE_DATA = Path("c:/Users/Ibrah/NetGuardian/data/ML-MATT-CompetitionQT2021_train.csv")
MODEL_PATH = Path("c:/Users/Ibrah/NetGuardian/backend/anomaly/pretrained_model.pkl")
SCALER_PATH = Path("c:/Users/Ibrah/NetGuardian/backend/anomaly/scaler.pkl")

# Mapping the real-world 4G columns to a signature we can use
COLUMNS = [
    'PRBUsageUL', 'PRBUsageDL', 'meanThr_DL', 'meanThr_UL', 
    'maxThr_DL', 'maxThr_UL', 'meanUE_DL', 'meanUE_UL', 
    'maxUE_DL', 'maxUE_UL'
]

def run_pretraining():
    if not KAGGLE_DATA.exists():
        logger.error(f"Kaggle data not found at {KAGGLE_DATA}")
        return

    logger.info("📡 Loading Kaggle 4G Cellular Anomaly Dataset...")
    df = pd.read_csv(KAGGLE_DATA, sep=';')
    
    # Pre-processing: Convert to numeric, handle NaNs
    for col in COLUMNS:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=COLUMNS)
    
    # Isolate "Normal" traffic for pre-training (Unusual == 0)
    normal_traffic = df[df['Unusual'] == 0][COLUMNS]
    logger.info(f"📊 Training on {len(normal_traffic)} normal network samples...")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(normal_traffic)

    # Train Isolation Forest (Pre-training phase)
    model = IsolationForest(
        n_estimators=100, 
        contamination=0.01, # We are training on mostly normal data
        random_state=42
    )
    model.fit(X_scaled)

    # Save Model and Scaler
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    logger.info(f"✅ Pretraining Complete. Model saved to {MODEL_PATH}")
    
    # Sanity Check: Feature Distributions
    logger.info("🔍 Feature Sanity Check (Mean Distributions):")
    for col in COLUMNS:
        logger.info(f"  - {col}: {normal_traffic[col].mean():.2f}")

if __name__ == "__main__":
    run_pretraining()
