import pandas as pd
from fastapi.testclient import TestClient

from backend.main import app
import backend.api.routes as routes


def _seed_test_state():
    routes._df = pd.DataFrame(
        [
            {
                "timestamp": pd.Timestamp.now(),
                "node_id": "Router-01",
                "latency_ms": 15.0,
                "throughput_mbps": 550.0,
                "packet_loss_pct": 0.2,
                "jitter_ms": 2.0,
                "connections": 140,
            }
            for _ in range(40)
        ]
    )
    routes._detector.fit(routes._df)


def test_health_endpoint():
    with TestClient(app) as client:
        _seed_test_state()
        resp = client.get("/api/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"


def test_metrics_history_endpoint():
    with TestClient(app) as client:
        _seed_test_state()
        resp = client.get("/api/metrics/history")
        assert resp.status_code == 200
        data = resp.json().get("data", [])
        assert isinstance(data, list)
        assert len(data) > 0


def test_nodes_status_endpoint():
    client = TestClient(app)
    resp = client.get("/api/nodes/status")
    assert resp.status_code == 200
    body = resp.json()
    assert "nodes" in body
    assert isinstance(body["nodes"], list)
    assert body["total"] == len(body["nodes"])
    # Every node must have the required fields
    for node in body["nodes"]:
        assert "node_id" in node
        assert "status" in node
        assert "criticality" in node
