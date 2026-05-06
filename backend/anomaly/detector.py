import numpy as np
import logging
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.1)
        self.training_data = []
        self.is_trained = False

    def train_step(self, features):
        if self.is_trained and len(self.training_data) > 50:
            baseline = np.mean(self.training_data[:50], axis=0)
            drift = np.linalg.norm(features - baseline)
            if drift > 15:
                logger.warning("🛡️ Sentinel Gate: High drift detected. Skipping online update.")
                return

        self.training_data.append(features)
        if len(self.training_data) >= 20:
            self.model.fit(np.array(self.training_data))
            self.is_trained = True

    def predict(self, features, node_status="Healthy"):
        """Decoupled Predictor: Accepts node_status as context instead of importing global sim."""
        if not self.is_trained:
            self.train_step(features)
            return False, 0.0

        score = self.model.score_samples([features])[0]
        anomaly = self.model.predict([features])[0] == -1

        # Mitigation-Aware Feedback (Feedback is now passed in)
        if anomaly and node_status != "Healthy":
            logger.info("Feedback Loop: Suppressing anomaly due to active mitigation.")
            anomaly = False
            score *= 0.5

        self.train_step(features)
        return anomaly, abs(score)
