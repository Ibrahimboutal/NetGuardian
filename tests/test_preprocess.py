import numpy as np

from backend.anomaly.preprocess import FeatureEngine


def test_feature_engine_vector_shape():
    engine = FeatureEngine(window_size=5)
    row = {
        "latency_ms": 10.0,
        "throughput_mbps": 500.0,
        "packet_loss_pct": 0.1,
        "jitter_ms": 2.0,
        "connections": 120,
    }
    vec = engine.process(row)
    assert isinstance(vec, np.ndarray)
    assert vec.shape[0] == 25

