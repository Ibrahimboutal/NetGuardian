import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from .preprocess import load_dataset, extract_features, row_to_dict, FEATURE_COLS
import logging

logger = logging.getLogger(__name__)

# Severity thresholds (tunable)
SEVERITY_RULES = {
    "latency_ms":       {"high": 200, "medium": 80},
    "packet_loss_pct":  {"high": 10,  "medium": 3},
    "jitter_ms":        {"high": 30,  "medium": 10},
    "throughput_mbps":  {"high": 300, "medium": 600},  # low is bad
    "connections":      {"high": 800, "medium": 400},
}


class AnomalyDetector:
    def __init__(self, contamination: float = 0.05, n_estimators: int = 100):
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=42,
        )
        self._trained = False

    def fit(self, df: pd.DataFrame):
        """Train the Isolation Forest on the full dataset."""
        X = extract_features(df)
        self.model.fit(X)
        self._trained = True
        logger.info("AnomalyDetector trained on %d samples.", len(df))

    def predict_row(self, row: pd.Series) -> dict:
        """
        Predict whether a single row is anomalous.
        Returns a structured event dict.
        """
        if not self._trained:
            raise RuntimeError("Detector not trained. Call fit() first.")

        X = np.array([[row[col] for col in FEATURE_COLS]])
        score = float(self.model.decision_function(X)[0])
        pred = int(self.model.predict(X)[0])  # -1 = anomaly, 1 = normal
        is_anomaly = pred == -1

        result = row_to_dict(row)
        result["anomaly"] = is_anomaly
        result["anomaly_score"] = round(-score, 4)   # higher = more anomalous

        if is_anomaly:
            result["severity"] = self._classify_severity(row)
            result["primary_metric"] = self._primary_metric(row)
        else:
            result["severity"] = "none"
            result["primary_metric"] = None

        return result

    def _classify_severity(self, row: pd.Series) -> str:
        """Rule-based severity on top of Isolation Forest output."""
        if row["latency_ms"] >= SEVERITY_RULES["latency_ms"]["high"]:
            return "high"
        if row["packet_loss_pct"] >= SEVERITY_RULES["packet_loss_pct"]["high"]:
            return "high"
        if row["jitter_ms"] >= SEVERITY_RULES["jitter_ms"]["high"]:
            return "high"
        if row["latency_ms"] >= SEVERITY_RULES["latency_ms"]["medium"]:
            return "medium"
        if row["packet_loss_pct"] >= SEVERITY_RULES["packet_loss_pct"]["medium"]:
            return "medium"
        return "low"

    def _primary_metric(self, row: pd.Series) -> str:
        """Identify which metric deviates most from its normal range."""
        deviations = {
            "latency_ms": row["latency_ms"] / 15,
            "packet_loss_pct": row["packet_loss_pct"] / 0.15,
            "jitter_ms": row["jitter_ms"] / 2.5,
            "connections": row["connections"] / 142,
        }
        return max(deviations, key=deviations.get)
