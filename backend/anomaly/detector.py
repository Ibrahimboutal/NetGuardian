# pyrefly: ignore [missing-import]
import numpy as np
import pandas as pd
import logging
from .preprocess import engine
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.1)
        self.training_data = []
        self.is_trained = False
        self.feature_names = [
            "latency_ms", "throughput_mbps", "packet_loss_pct", "jitter_ms", "connections",
            "latency_avg", "throughput_avg", "packet_loss_avg", "jitter_avg", "connections_avg",
            "latency_std", "throughput_std", "packet_loss_std", "jitter_std", "connections_std",
            "latency_delta", "throughput_delta", "packet_loss_delta", "jitter_delta", "connections_delta",
            "latency_trend", "throughput_trend", "packet_loss_trend", "jitter_trend", "connections_trend"
        ]

    def fit(self, df: pd.DataFrame):
        logger.info("🏭 Initializing Sentinel via batch training...")

        features_list = []

        for _, row in df.iterrows():
            data = row.to_dict()

            # Strip non-numeric values (timestamps, strings, etc.)
            clean_data = {
                k: v for k, v in data.items()
                if isinstance(v, (int, float, np.number))
            }

            features = engine.process(clean_data)
            features_list.append(features)

        X = np.array(features_list, dtype=float)

        self.model.fit(X)
        self.is_trained = True
        self.training_data = features_list[-500:]

        self.save_model()

    def train_step(self, features):
        self.training_data.append(features)

        if len(self.training_data) >= 20:
            X = np.array(self.training_data)
            self.model.fit(X)
            self.is_trained = True

    def save_model(self):
        # Placeholder for model persistence
        logger.info("💾 Model state captured.")

    def predict(self, features: np.ndarray, node_id: str = "Unknown") -> tuple:
        from backend.agents.tools import sim  # avoid circular import

        if not self.is_trained:
            self.train_step(features)
            return False, 0.0, "normal", []

        X = features.reshape(1, -1)

        score = float(self.model.score_samples(X)[0])
        is_anomaly = bool(self.model.predict(X)[0] == -1)

        # --- Feedback loop (mitigation awareness) ---
        node_state = sim.node_states.get(node_id, {})
        status = node_state.get("status", "Healthy")

        if is_anomaly and status in ["Isolated", "Throttled", "Rerouted"]:
            logger.info(f"🛡️ Suppressing anomaly on {node_id} (status={status})")
            is_anomaly = False
            score *= 0.5

        # --- Attribution ---
        attribution = []

        if is_anomaly and len(self.training_data) > 0:
            train_mean = np.mean(self.training_data, axis=0)
            train_std = np.std(self.training_data, axis=0) + 1e-6

            z_scores = np.abs((features - train_mean) / train_std)
            top_indices = np.argsort(z_scores)[-3:][::-1]

            attribution = [
                self.feature_names[i]
                for i in top_indices
                if i < len(self.feature_names) and z_scores[i] > 2.0
            ]

        # --- Severity ---
        severity = "normal"
        if is_anomaly:
            if score < -0.65:
                severity = "critical"
            elif score < -0.55:
                severity = "high"
            else:
                severity = "medium"

        self.train_step(features)

        return is_anomaly, abs(score), severity, attribution

    def predict_row(self, row: pd.Series) -> dict:
        """
        High-level wrapper for routes.py.
        Handles row conversion, feature engineering, and returns a UI-ready dict.
        """
        data = row.to_dict()
        
        # Strip non-numeric values for the model
        clean_data = {
            k: v for k, v in data.items()
            if isinstance(v, (int, float, np.number))
        }

        # Run feature engine (temporal awareness)
        features = engine.process(clean_data)
        
        # Predict
        node_id = data.get("node_id", "Router-14")
        is_anomaly, score, severity, attribution = self.predict(features, node_id=node_id)

        # Build payload
        return {
            "timestamp": str(data.get("timestamp", pd.Timestamp.now())),
            "anomaly": is_anomaly,
            "score": round(score, 4),
            "severity": severity,
            "attribution": attribution,
            "metrics": clean_data,
            "node_id": node_id
        }

detector = AnomalyDetector()