from backend.events.trigger import trigger_agent_pipeline


def test_trigger_pipeline_returns_agent_bundle_for_anomaly():
    event = {
        "timestamp": "2026-01-01T00:00:00Z",
        "anomaly": True,
        "score": 0.9,
        "anomaly_score": 0.9,
        "severity": "high",
        "attribution": ["latency_ms"],
        "primary_metric": "latency_ms",
        "metrics": {"latency_ms": 380.0},
        "node_id": "Router-14",
    }
    out = trigger_agent_pipeline(event)
    assert out.get("agents") is not None
    assert out.get("simulation") is not None
    assert out.get("incident_state") == "open"

