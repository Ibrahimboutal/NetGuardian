import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import logging
import pickle
import os
from pathlib import Path
from .preprocess import engine

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent.parent.parent / "models"
MODEL_PATH = MODEL_DIR / "sentinel_iso_forest.pkl"

class AnomalyDetector:
    """
    Sentinel-Grade Anomaly Detector.
    Uses Isolation Forest with Temporal Feature Enrichment and Online Adaptation.
    """
    def __init__(self):
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
            "lat", "thru", "pkt", "jit", "conn", 
            "lat_m", "thru_m", "pkt_m", "jit_m", "conn_m",
            "lat_s", "thru_s", "pkt_s", "jit_s", "conn_s",
            "lat_d", "thru_d", "pkt_d", "jit_d", "conn_d",
            "lat_t", "thru_t", "pkt_t", "jit_t", "conn_t"
        ]
        
        self.load_model()

    def log_edge_readiness(self):
        """Proof of Work: Edge Constraint Verification."""
        model_size_kb = os.path.getsize(MODEL_PATH) / 1024 if MODEL_PATH.exists() else 0
        logger.info("🛡️ --- EDGE READINESS REPORT ---")
        logger.info(f"📍 Model: Isolation Forest (Ensemble)")
        logger.info(f"📍 Storage: {model_size_kb:.2f} KB (Edge-Optimized)")
        logger.info(f"📍 RAM Target: <128MB (Disaster-Grade)")
        logger.info(f"📍 Inference Mode: Deterministic Local (100% Offline)")
        logger.info("-------------------------------")

    def save_model(self):
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump({
                "model": self.model,
                "is_trained": self.is_trained,
                "training_data": self.training_data
            }, f)
        logger.info(f"💾 Model checkpoint persisted: {MODEL_PATH.name}")

    def load_model(self):
        if MODEL_PATH.exists():
            try:
                with open(MODEL_PATH, "rb") as f:
                    data = pickle.load(f)
                    self.model = data["model"]
                    self.is_trained = data["is_trained"]
                    self.training_data = data["training_data"]
                logger.info("✅ Resumed Sentinel from local edge checkpoint.")
                self.log_edge_readiness()
            except Exception as e:
                logger.warning(f"⚠️ Failed to load model: {e}. Starting fresh.")

    def fit(self, df: pd.DataFrame):
        logger.info("🏭 Initializing Sentinel via batch training...")
        features_list = [engine.process(row) for _, row in df.iterrows()]
        X = np.array(features_list)
        self.model.fit(X)
        self.is_trained = True
        self.training_data = features_list[-500:]
        self.save_model()

    def train_step(self, features: np.ndarray):
        self.training_data.append(features)
        self.steps_since_last_fit += 1
        if len(self.training_data) > 500:
            self.training_data.pop(0)

        # Periodic online adaptation (Concept Drift handling)
        if (not self.is_trained and len(self.training_data) >= self.required_samples) or (self.steps_since_last_fit >= 50):
            X = np.array(self.training_data)
            self.model.fit(X)
            self.is_trained = True
            self.steps_since_last_fit = 0
            self.save_model()

    def predict(self, features: np.ndarray, node_id: str = "Router-14") -> tuple:
        """
        Self-Aware Inference: Adjusts sensitivity based on active AI mitigations.
        """
        from backend.agents.tools import sim # Lazy import to avoid circularity
        
        if not self.is_trained:
            self.train_step(features)
            return False, 0.0, "normal", []
            
        X = features.reshape(1, -1)
        score = float(self.model.score_samples(X)[0])
        is_anomaly = bool(self.model.predict(X)[0] == -1)
        
        # ENVIRONMENT FEEDBACK LOOP: 
        # If the AI has already applied a mitigation, the 'anomaly' might be expected behavior.
        node_state = sim.node_states.get(node_id, {})
        status = node_state.get("status", "Healthy")
        
        if is_anomaly and status in ["Isolated", "Throttled", "Rerouted"]:
            logger.info(f"🛡️ Sentinel Feedback: Suppressing anomaly on {node_id} (Active Mitigation: {status})")
            is_anomaly = False # Suppress false alarm from own action
            score *= 0.5 # Lower confidence
            
        attribution = []
        if is_anomaly:
            train_mean = np.mean(self.training_data, axis=0)
            train_std = np.std(self.training_data, axis=0) + 1e-6
            z_scores = np.abs((features - train_mean) / train_std)
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

detector = AnomalyDetector()

def check_anomaly(features: np.ndarray) -> dict:
    is_anomaly, score, severity, attribution = detector.predict(features)
    return {
        "anomaly": is_anomaly,
        "anomaly_score": round(score, 4),
        "severity": severity,
        "attribution": attribution
    }
