import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.api import routes
from backend.main import app


class BackendSmokeTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        routes._incident_log.clear()
        routes._incident_log_loaded = False
        routes._benchmark_cache = None

    def test_health_endpoint_returns_operational_snapshot(self):
        with patch.object(routes, "_ensure_trained", return_value=None):
            response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertIn("dataset_rows", payload)
        self.assertIn("incidents_recorded", payload)

    def test_inject_anomaly_uses_default_core_node(self):
        with patch.object(routes, "_ensure_trained", return_value=None), patch.object(
            routes,
            "trigger_agent_pipeline",
            side_effect=lambda event, progress_cb=None: {
                **event,
                "agents": {"diagnosis": "ok", "recommendation": "ok", "explanation": "ok"},
            },
        ):
            response = self.client.post("/api/inject-anomaly")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["node_id"], "Core-DC-01")
        self.assertTrue(payload["anomaly"])

    def test_benchmark_result_is_cached(self):
        class FakeEvaluator:
            calls = 0

            def run_benchmark(self, num_iterations=120):
                FakeEvaluator.calls += 1
                return {
                    "net_guardian_ai": {"precision": 0.9, "recall": 0.8, "avg_lag_sec": 10},
                    "adaptive_ma_baseline": {"precision": 0.5, "recall": 0.4, "avg_lag_sec": 18},
                }

        with patch.object(routes, "_ensure_trained", return_value=None), patch("backend.evaluation.NetGuardianEvaluator", FakeEvaluator):
            first = routes.evaluation_benchmark(refresh=True)
            second = routes.evaluation_benchmark(refresh=False)

        self.assertEqual(FakeEvaluator.calls, 1)
        self.assertEqual(first, second)
        self.assertIn("results", first)

    def test_record_incident_persists_anomaly(self):
        event = {
            "anomaly": True,
            "severity": "high",
            "primary_metric": "latency_ms",
            "node_id": "Core-DC-01",
            "anomaly_score": 0.91,
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            original_path = routes.INCIDENT_LOG_PATH
            routes.INCIDENT_LOG_PATH = Path(tmp_dir) / "incident_log.jsonl"
            try:
                routes._record_incident(event)
                routes._incident_log_loaded = False
                routes._incident_log.clear()
                routes._load_incident_log()
            finally:
                routes.INCIDENT_LOG_PATH = original_path

        self.assertTrue(routes._incident_log)
        self.assertEqual(routes._incident_log[-1]["node_id"], "Core-DC-01")


if __name__ == "__main__":
    unittest.main()
