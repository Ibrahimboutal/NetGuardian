import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

FEATURE_COLS = ["latency_ms", "throughput_mbps", "packet_loss_pct", "jitter_ms", "connections"]


def load_dataset(csv_path: str) -> pd.DataFrame:
    """Load and parse the network traffic CSV."""
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def extract_features(df: pd.DataFrame) -> np.ndarray:
    """Return a scaled feature matrix for anomaly detection."""
    X = df[FEATURE_COLS].fillna(0).values
    scaler = StandardScaler()
    return scaler.fit_transform(X)


def row_to_dict(row: pd.Series) -> dict:
    """Convert a DataFrame row to a clean metric dict."""
    return {
        "timestamp": str(row["timestamp"]),
        "latency_ms": float(row["latency_ms"]),
        "throughput_mbps": float(row["throughput_mbps"]),
        "packet_loss_pct": float(row["packet_loss_pct"]),
        "jitter_ms": float(row["jitter_ms"]),
        "connections": int(row["connections"]),
    }
