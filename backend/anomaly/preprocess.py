import pandas as pd
import numpy as np
from collections import deque

def load_dataset(path: str) -> pd.DataFrame:
    """Utility to load the simulation dataset."""
    with open(path, 'r') as f:
        first_line = f.readline()
    
    if ';' in first_line:
        df = pd.read_csv(path, sep=';')
    else:
        df = pd.read_csv(path)
        
    if 'Time' in df.columns and 'CellName' in df.columns:
        df = df.rename(columns={
            'Time': 'timestamp',
            'CellName': 'node_id',
            'meanThr_DL': 'latency_ms',
            'PRBUsageDL': 'throughput_mbps',
            'PRBUsageUL': 'packet_loss_pct',
            'maxThr_DL': 'jitter_ms',
            'meanUE_DL': 'connections'
        })
        today = pd.Timestamp.now().strftime('%Y-%m-%d ')
        df['timestamp'] = pd.to_datetime(today + df['timestamp'].astype(str))
    else:
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    if 'node_id' not in df.columns:
        node_ids = [
            'Router-01', 'Router-02', 'Router-03', 'Router-04', 'Router-05',
            'Router-14', 'Switch-02', 'Core-DC-01', 'Substation-Alpha',
            'Substation-Beta', 'Regional-Hub-North', 'Regional-Hub-South',
            'Node-A', 'Node-B', 'Node-X', 'Node-Y', 'Backup-Vault-01'
        ]
        df['node_id'] = [node_ids[i % len(node_ids)] for i in range(len(df))]
        
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
