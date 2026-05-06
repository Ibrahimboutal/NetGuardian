import numpy as np
import logging
from sklearn.ensemble import IsolationForest
from .tools import sim

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
                logger.warning("Drift too high, skipping update")
                return

        self.training_data.append(features)

        if len(self.training_data) >= 20:
            self.model.fit(np.array(self.training_data))
            self.is_trained = True

    def predict(self, features, node_id="Router-14"):
        if not self.is_trained:
            self.train_step(features)
            return False, 0.0

        score = self.model.score_samples([features])[0]
        anomaly = self.model.predict([features])[0] == -1

        state = sim.node_states.get(node_id, {})
        if anomaly and state.get("status") != "Healthy":
            anomaly = False
            score *= 0.5

        self.train_step(features)

        return anomaly, abs(score)
