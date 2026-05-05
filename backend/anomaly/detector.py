import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import logging
from .preprocess import engine

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Sentinel-Grade Anomaly Detector.
    Uses Isolation Forest with Temporal Feature Enrichment and Feature Attribution.
    """
    def __init__(self):
        # 25 features from the FeatureEngine
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42
        )
        self.is_trained = False
        self.training_data = []
        self.required_samples = 20
        self.steps_since_last_fit = 0
        
        self.feature_names = [
            "lat", "thru", "pkt", "jit", "conn", # Latest
            "lat_m", "thru_m", "pkt_m", "jit_m", "conn_m", # Mean
            "lat_s", "thru_s", "pkt_s", "jit_s", "conn_s", # Std
            "lat_d", "thru_d", "pkt_d", "jit_d", "conn_d", # Delta
            "lat_t", "thru_t", "pkt_t", "jit_t", "conn_t"  # Trend
        ]

    def fit(self, df: pd.DataFrame):
        """Batch training for initial setup."""
        logger.info("Initializing Sentinel Model via batch training...")
        features_list = []
        for _, row in df.iterrows():
            features_list.append(engine.process(row))
        
        X = np.array(features_list)
        self.model.fit(X)
        self.is_trained = True
        self.training_data = features_list[-500:]

    def train_step(self, features: np.ndarray):
        """Online training/adaptation."""
        self.training_data.append(features)
        self.steps_since_last_fit += 1
        if len(self.training_data) > 500:
            self.training_data.pop(0)

        if (not self.is_trained and len(self.training_data) >= self.required_samples) or (self.steps_since_last_fit >= 50):
            X = np.array(self.training_data)
            self.model.fit(X)
            self.is_trained = True
            self.steps_since_last_fit = 0

    def predict(self, features: np.ndarray) -> tuple:
        if not self.is_trained:
            self.train_step(features)
            return False, 0.0, "normal", []
            
        X = features.reshape(1, -1)
        score = float(self.model.score_samples(X)[0])
        is_anomaly = bool(self.model.predict(X)[0] == -1)
        
        attribution = []
        if is_anomaly:
            # Simple Feature Attribution: Identify which features deviated most from training mean
            train_mean = np.mean(self.training_data, axis=0)
            train_std = np.std(self.training_data, axis=0) + 1e-6
            z_scores = np.abs((features - train_mean) / train_std)
            
            # Get top 3 features by deviation
            top_indices = np.argsort(z_scores)[-3:][::-1]
            attribution = [self.feature_names[i] for i in top_indices if z_scores[i] > 2.0]

        severity = "normal"
        if is_anomaly:
            if score < -0.65: severity = "critical"
            elif score < -0.55: severity = "high"
            else: severity = "medium"
            
        self.train_step(features)
        return is_anomaly, abs(score), severity, attribution

    def predict_row(self, row: pd.Series) -> dict:
        """Shim for API routes."""
        features = engine.process(row)
        is_anomaly, score, severity, attribution = self.predict(features)
        
        res = row.to_dict()
        if 'timestamp' in res:
            res['timestamp'] = str(res['timestamp'])
            
        res.update({
            "anomaly": is_anomaly,
            "anomaly_score": round(score, 4),
            "severity": severity,
            "attribution": attribution,
            "primary_metric": attribution[0] if attribution else "latency_ms"
        })
        return res

# Singleton
detector = AnomalyDetector()

def check_anomaly(features: np.ndarray) -> dict:
    is_anomaly, score, severity, attribution = detector.predict(features)
    return {
        "anomaly": is_anomaly,
        "anomaly_score": round(score, 4),
        "severity": severity,
        "attribution": attribution
    }
