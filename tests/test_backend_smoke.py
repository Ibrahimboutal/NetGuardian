import unittest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from backend.api import routes
from backend.main import app


class BackendSmokeTests(unittest.TestCase):
    def setUp(self):
        self._ctx = TestClient(app)
        self.client = self._ctx.__enter__()
        # Clear cache for deterministic testing
        routes._benchmark_cache = None

    def tearDown(self):
        routes._benchmark_cache = None
        self._ctx.__exit__(None, None, None)

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
                "incident_id": "test-id-123",
                "anomaly": True
            },
        ), patch("backend.api.routes.record_incident", side_effect=lambda x: None):
            response = self.client.post("/api/inject-anomaly")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["node_id"], "Core-DC-01")
        self.assertTrue(payload["anomaly"])

    def test_benchmark_result_is_cached(self):
        class FakeEvaluator:
            calls = 0

            def run_benchmark(self, num_iterations=120, seed=42):
                FakeEvaluator.calls += 1
                return {
                    "net_guardian_ai": {"precision": 0.9, "recall": 0.8, "avg_lag_sec": 10},
                    "adaptive_ma_baseline": {"precision": 0.5, "recall": 0.4, "avg_lag_sec": 18},
                }

        mock_request = MagicMock()
        with patch.object(routes, "_ensure_trained", return_value=None), patch("backend.evaluation.NetGuardianEvaluator", FakeEvaluator):
            first = routes.evaluation_benchmark(request=mock_request, refresh=True)
            second = routes.evaluation_benchmark(request=mock_request, refresh=False)

        self.assertEqual(FakeEvaluator.calls, 1)
        self.assertEqual(first, second)
        self.assertIn("results", first)

    def test_record_incident_calls_db(self):
        event = {
            "anomaly": True,
            "severity": "high",
            "primary_metric": "latency_ms",
            "node_id": "Core-DC-01",
            "anomaly_score": 0.91,
        }

        with patch("backend.api.routes.record_incident") as mock_record:
            asyncio.run(routes._record_incident(event))
            mock_record.assert_called_once()
            args, _ = mock_record.call_args
            self.assertEqual(args[0]["node_id"], "Core-DC-01")
            self.assertIn("incident_id", args[0])


if __name__ == "__main__":
    unittest.main()
