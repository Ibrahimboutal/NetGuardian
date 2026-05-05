import pandas as pd
import numpy as np
from collections import deque

class FeatureEngine:
    """
    Advanced Preprocessing for Network Telemetry.
    Adds temporal awareness via rolling windows and trend detection.
    """
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)
        self.columns = ["latency_ms", "throughput_mbps", "packet_loss_pct", "jitter_ms", "connections"]

    def process(self, raw_data: dict) -> np.ndarray:
        # Convert dict to flat list in correct order
        current_values = [raw_data.get(c, 0) for c in self.columns]
        self.history.append(current_values)
        
        # Convert history to DataFrame for easy rolling calcs
        df = pd.DataFrame(list(self.history), columns=self.columns)
        
        # Base features
        latest = df.iloc[-1].values
        
        # Rolling features
        means = df.mean().values
        stds = df.fillna(0).std().values
        
        # Delta features (Current - Previous)
        if len(df) > 1:
            deltas = df.iloc[-1].values - df.iloc[-2].values
        else:
            deltas = np.zeros(len(self.columns))
            
        # Trend detection (Increasing/Decreasing)
        # 1 if increasing for last 3 steps, -1 if decreasing, 0 otherwise
        trends = []
        for col in self.columns:
            if len(df) >= 3:
                vals = df[col].tail(3).values
                if vals[0] < vals[1] < vals[2]:
                    trends.append(1)
                elif vals[0] > vals[1] > vals[2]:
                    trends.append(-1)
                else:
                    trends.append(0)
            else:
                trends.append(0)
        
        # Combine all features into one vector
        # [Latest(5), Means(5), Stds(5), Deltas(5), Trends(5)] = 25 features
        combined = np.concatenate([latest, means, stds, deltas, trends])
        
        # Replace NaNs with 0
        return np.nan_to_num(combined)

# Singleton instance
engine = FeatureEngine()

def preprocess_telemetry(raw_data: dict) -> np.ndarray:
    """Wrapper for the FeatureEngine."""
    return engine.process(raw_data)
