import pandas as pd

from backend.anomaly.detector import AnomalyDetector


def test_detector_predict_row_payload_keys():
    detector = AnomalyDetector()
    df = pd.DataFrame(
        [
            {
                "timestamp": pd.Timestamp.now(),
                "node_id": "Router-01",
                "latency_ms": 10.0,
                "throughput_mbps": 600.0,
                "packet_loss_pct": 0.1,
                "jitter_ms": 1.0,
                "connections": 100,
            }
            for _ in range(25)
        ]
    )
    detector.fit(df)
    row = df.iloc[0]
    event = detector.predict_row(row)
    assert "anomaly" in event
    assert "anomaly_score" in event
    assert "severity" in event
    assert "primary_metric" in event


def test_detector_resilience_to_corrupted_model():
    from unittest.mock import patch
    detector = AnomalyDetector()
    df = pd.DataFrame([{"latency_ms": 10.0}] * 20)
    
    # Mock model.fit to fail once with AttributeError (simulating corrupted state)
    with patch.object(detector.model, "fit", side_effect=[AttributeError("corrupted"), None]):
        # This should trigger the try-except in detector.fit, reset the model, and succeed on retry
        detector.fit(df)
        
    assert detector.is_trained is True

