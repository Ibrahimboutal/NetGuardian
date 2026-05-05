import numpy as np
from sklearn.ensemble import IsolationForest
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Sentinel-Grade Anomaly Detector.
    Uses Isolation Forest with Temporal Feature Enrichment.
    """
    def __init__(self):
        # 25 features from the new FeatureEngine
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42
        )
        self.is_trained = False
        self.training_data = []
        self.required_samples = 20  # Warm-up period

    def train_step(self, features: np.ndarray):
        """Online training/adaptation."""
        self.training_data.append(features)
        
        # Keep training data windowed to avoid memory leak
        if len(self.training_data) > 500:
            self.training_data.pop(0)

        if len(self.training_data) >= self.required_samples:
            X = np.array(self.training_data)
            self.model.fit(X)
            self.is_trained = True

    def predict(self, features: np.ndarray) -> tuple:
        """
        Returns (is_anomaly, score, severity)
        """
        if not self.is_trained:
            self.train_step(features)
            return False, 0.0, "normal"

        # Reshape for single prediction
        X = features.reshape(1, -1)
        
        # score_samples returns negative values (lower is more anomalous)
        score = float(self.model.score_samples(X)[0])
        
        # IsolationForest decision_function: <0 is anomaly
        is_anomaly = bool(self.model.predict(X)[0] == -1)
        
        # Calculate severity based on score
        # score usually ranges from -1 to 0
        severity = "normal"
        if is_anomaly:
            if score < -0.65:
                severity = "critical"
            elif score < -0.55:
                severity = "high"
            else:
                severity = "medium"

        # Continuous learning
        self.train_step(features)
        
        return is_anomaly, abs(score), severity

# Singleton
detector = AnomalyDetector()

def check_anomaly(features: np.ndarray) -> dict:
    is_anomaly, score, severity = detector.predict(features)
    return {
        "anomaly": is_anomaly,
        "anomaly_score": round(score, 4),
        "severity": severity
    }
