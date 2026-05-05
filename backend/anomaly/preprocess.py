import pandas as pd
import numpy as np
from collections import deque

def load_dataset(path: str) -> pd.DataFrame:
    """Utility to load the simulation dataset."""
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

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
        # Handle both dict and Series
        if hasattr(raw_data, 'to_dict'):
            raw_data = raw_data.to_dict()
            
        current_values = [raw_data.get(c, 0) for c in self.columns]
        self.history.append(current_values)
        
        df = pd.DataFrame(list(self.history), columns=self.columns)
        latest = df.iloc[-1].values
        means = df.mean().values
        stds = df.fillna(0).std().values
        
        if len(df) > 1:
            deltas = df.iloc[-1].values - df.iloc[-2].values
        else:
            deltas = np.zeros(len(self.columns))
            
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
        
        combined = np.concatenate([latest, means, stds, deltas, trends])
        return np.nan_to_num(combined)

# Singleton instance
engine = FeatureEngine()

def preprocess_telemetry(raw_data: dict) -> np.ndarray:
    """Wrapper for the FeatureEngine."""
    return engine.process(raw_data)
