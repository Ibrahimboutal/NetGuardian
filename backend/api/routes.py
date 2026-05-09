import asyncio
import json
import logging
from pathlib import Path
from collections import Counter

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from backend.anomaly.preprocess import load_dataset
from backend.anomaly.detector import AnomalyDetector
from backend.events.trigger import trigger_agent_pipeline
from backend.data_factory import industrialDataFactory

logger = logging.getLogger(__name__)
router = APIRouter()

import threading
from datetime import datetime, timezone

# --- Shared state ---
DATA_PATH = Path(__file__).parent.parent.parent / "data" / "ML-MATT-CompetitionQT2021_train.csv"
INCIDENT_LOG_PATH = Path(__file__).parent.parent.parent / "data" / "incident_log.jsonl"
_df = None
_detector = AnomalyDetector()
_stream_active = False
_train_lock = threading.Lock()
_incident_log = []
_benchmark_cache = None
_incident_log_loaded = False


def _load_incident_log():
    global _incident_log_loaded
    if _incident_log_loaded:
        return

    if INCIDENT_LOG_PATH.exists():
        try:
            with INCIDENT_LOG_PATH.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        _incident_log.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
                del _incident_log[:-100]
        except OSError:
            logger.warning("Unable to load incident log from disk.")

    _incident_log_loaded = True


def _append_incident_to_disk(event: dict):
    try:
        INCIDENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with INCIDENT_LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, default=str) + "\n")
    except OSError:
        logger.warning("Unable to persist incident log entry.")


def _record_incident(event: dict):
    _load_incident_log()
    if event and event.get("anomaly"):
        _incident_log.append(event)
        del _incident_log[:-100]
        _append_incident_to_disk(event)


def _build_summary() -> dict:
    total = len(_incident_log)
    severity_counts = Counter(item.get("severity", "unknown") for item in _incident_log)
    primary_metrics = Counter(item.get("primary_metric", "unknown") for item in _incident_log)
    avg_score = 0.0
    if total:
        scores = [float(item.get("anomaly_score", item.get("score", 0)) or 0) for item in _incident_log]
        avg_score = sum(scores) / len(scores)
    return {
        "total_incidents": total,
        "severity_counts": dict(severity_counts),
        "primary_metrics": dict(primary_metrics),
        "average_score": round(avg_score, 4),
        "stream_active": _stream_active,
    }


def _build_insights() -> dict:
    _load_incident_log()
    recent = _incident_log[-20:]
    recent_total = len(recent)

    if not recent_total:
        return {
            "recurring_case": None,
            "recurring_case_count": 0,
            "recurring_case_rate": 0.0,
            "dominant_metric": None,
            "forecast": "Insufficient incident memory",
            "recurrence_window": recent_total,
            "top_cases": [],
        }

    case_counter = Counter(
        (item.get("experience") or {}).get("id") or item.get("primary_metric", "unknown")
        for item in recent
    )
    metric_counter = Counter(item.get("primary_metric", "unknown") for item in recent)
    top_case, top_case_count = case_counter.most_common(1)[0]
    dominant_metric, dominant_metric_count = metric_counter.most_common(1)[0]
    recurring_rate = top_case_count / recent_total
    forecast = "Monitor for repetition" if recurring_rate < 0.35 else "Recurring failure mode detected"

    top_cases = []
    for case_id, count in case_counter.most_common(3):
        top_cases.append({
            "id": case_id,
            "count": count,
            "share": round(count / recent_total, 2),
        })

    return {
        "recurring_case": top_case,
        "recurring_case_count": top_case_count,
        "recurring_case_rate": round(recurring_rate, 2),
        "dominant_metric": dominant_metric,
        "dominant_metric_count": dominant_metric_count,
        "forecast": forecast,
        "recurrence_window": recent_total,
        "top_cases": top_cases,
    }


def _build_forecast() -> dict:
    _load_incident_log()
    recent = _incident_log[-10:]
    if not recent:
        return {
            "horizon_sec": 60,
            "risk_level": "unknown",
            "confidence": 0.0,
            "next_metric": None,
            "next_action": "Collect more telemetry",
            "reason": "No incident memory available yet.",
        }

    severity_score = {
        "critical": 1.0,
        "high": 0.8,
        "medium": 0.55,
        "low": 0.3,
        "normal": 0.1,
        "unknown": 0.2,
    }
    metric_counter = Counter(item.get("primary_metric", "unknown") for item in recent)
    case_counter = Counter((item.get("experience") or {}).get("id") or item.get("primary_metric", "unknown") for item in recent)
    avg_severity = sum(severity_score.get(item.get("severity", "unknown"), 0.2) for item in recent) / len(recent)
    top_metric, top_metric_count = metric_counter.most_common(1)[0]
    top_case, top_case_count = case_counter.most_common(1)[0]

    recurrence_strength = top_case_count / len(recent)
    confidence = min(0.95, round((avg_severity * 0.55) + (recurrence_strength * 0.45), 2))

    if confidence >= 0.75:
        risk_level = "high"
        next_action = "Prepare isolation or throttling"
    elif confidence >= 0.45:
        risk_level = "medium"
        next_action = "Increase monitoring and verify topology"
    else:
        risk_level = "low"
        next_action = "Continue live monitoring"

    if top_case_count >= 3:
        reason = f"Repeated case {top_case} appears {top_case_count} times in the latest memory window."
    else:
        reason = f"The dominant pressure is on {top_metric}, with {top_metric_count} recent hits and rising incident severity."

    return {
        "horizon_sec": 60,
        "risk_level": risk_level,
        "confidence": confidence,
        "next_metric": top_metric,
        "next_case": top_case,
        "next_action": next_action,
        "reason": reason,
        "window_size": len(recent),
    }


def _build_cascade_timeline() -> dict:
    _load_incident_log()
    recent = _incident_log[-8:]
    if not recent:
        return {
            "horizon_sec": 60,
            "focus_node": None,
            "risk_level": "unknown",
            "spread_target": None,
            "steps": [],
            "summary": "No incident memory available yet.",
        }

    metric_counter = Counter(item.get("primary_metric", "unknown") for item in recent)
    node_counter = Counter(item.get("node_id", "Router-14") for item in recent)
    case_counter = Counter((item.get("experience") or {}).get("id") or item.get("primary_metric", "unknown") for item in recent)
    severity_weights = {
        "critical": 3,
        "high": 2,
        "medium": 1,
        "low": 0.5,
        "normal": 0.2,
        "unknown": 0.4,
    }

    focus_node, focus_count = node_counter.most_common(1)[0]
    spread_target, spread_count = metric_counter.most_common(1)[0]
    recurring_case, recurring_case_count = case_counter.most_common(1)[0]
    severity_pressure = sum(severity_weights.get(item.get("severity", "unknown"), 0.4) for item in recent) / len(recent)

    cascade_score = min(1.0, round((focus_count / len(recent)) * 0.35 + (spread_count / len(recent)) * 0.35 + (severity_pressure / 3.0) * 0.3, 2))
    if cascade_score >= 0.72:
        risk_level = "high"
        spread_verb = "propagate"
        action = "preemptive isolation"
    elif cascade_score >= 0.42:
        risk_level = "medium"
        spread_verb = "drift"
        action = "tighten routing and watch dependency edges"
    else:
        risk_level = "low"
        spread_verb = "stay localized"
        action = "keep sampling the active node"

    steps = [
        {
            "window_sec": 0,
            "label": "Trigger",
            "node": focus_node,
            "signal": spread_target,
            "effect": "Current pressure concentrates on the epicenter.",
        },
        {
            "window_sec": 20,
            "label": "Cascade edge",
            "node": focus_node,
            "signal": recurring_case,
            "effect": f"Recent cases suggest the failure can {spread_verb} into the repeating pattern.",
        },
        {
            "window_sec": 40,
            "label": "Containment horizon",
            "node": f"{focus_node} / perimeter",
            "signal": spread_target,
            "effect": f"Recommended response: {action} before the next wave expands.",
        },
    ]

    return {
        "horizon_sec": 60,
        "focus_node": focus_node,
        "focus_count": focus_count,
        "spread_target": spread_target,
        "spread_count": spread_count,
        "recurring_case": recurring_case,
        "recurring_case_count": recurring_case_count,
        "risk_level": risk_level,
        "cascade_score": cascade_score,
        "steps": steps,
        "summary": f"{risk_level.upper()} cascade risk centered on {focus_node} with pressure on {spread_target}.",
    }


def _ensure_trained():
    global _df, _detector
    _load_incident_log()
    if _df is not None:
        return
        
    with _train_lock:
        if _df is not None:
            return
            
        # WINNER MOVE: Generate high-fidelity industrial data on the fly for the demo
        if not DATA_PATH.exists():
            logger.info("🏭 Generating Industrial-Grade Telemetry for the demo...")
            factory = industrialDataFactory(duration_hours=24)
            _df = factory.generate(anomaly_rate=0.03) # Balanced for demo
            DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
            _df.to_csv(str(DATA_PATH), index=False)
        else:
            _df = load_dataset(str(DATA_PATH))
            
        _detector.fit(_df)


@router.get("/api/health")
def health():
    _ensure_trained()
    return {
        "status": "ok",
        "model": "IsolationForest",
        "ai": "Gemma (Ollama)",
        "dataset_rows": int(len(_df)) if _df is not None else 0,
        "incidents_recorded": len(_incident_log),
        "stream_active": _stream_active,
    }


@router.get("/api/metrics/history")
def metrics_history():
    """Return the full dataset for initial chart rendering."""
    _ensure_trained()
    # Take last 100 points for initial UI load
    records = _df.tail(100).to_dict(orient="records")
    for r in records:
        r["timestamp"] = str(r["timestamp"])
    return {"data": records}


@router.get("/api/incidents/recent")
def recent_incidents(limit: int = 20):
    """Return the most recent incident payloads for operator review."""
    _load_incident_log()
    limit = max(1, min(limit, 100))
    return {"data": _incident_log[-limit:]}


@router.get("/api/system/summary")
def system_summary():
    """Return a compact operational summary for the demo and writeup."""
    _ensure_trained()
    summary = _build_summary()
    summary["insights"] = _build_insights()
    summary["forecast"] = _build_forecast()
    summary["cascade"] = _build_cascade_timeline()
    summary["data_points"] = int(len(_df)) if _df is not None else 0
    summary["columns"] = list(_df.columns) if _df is not None else []
    return summary


@router.get("/api/incidents/insights")
def incident_insights():
    """Return recurring-pattern insights derived from the incident memory."""
    return _build_insights()


@router.get("/api/incidents/forecast")
def incident_forecast():
    """Return a short-horizon forecast based on recent incident memory."""
    forecast = _build_forecast()
    forecast["cascade"] = _build_cascade_timeline()
    return forecast


@router.get("/api/incidents/export")
def export_incidents():
    """Return a single JSON report that can be downloaded by the frontend."""
    _load_incident_log()
    _ensure_trained()
    return {
        "summary": _build_summary(),
        "insights": _build_insights(),
        "forecast": _build_forecast(),
        "cascade": _build_cascade_timeline(),
        "recent_incidents": _incident_log[-100:],
        "benchmark": _benchmark_cache,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/evaluation/benchmark")
def evaluation_benchmark(refresh: bool = False):
    """Run or return a cached anomaly-detection benchmark."""
    global _benchmark_cache

    if _benchmark_cache is not None and not refresh:
        return _benchmark_cache

    _ensure_trained()

    from backend.evaluation import NetGuardianEvaluator

    evaluator = NetGuardianEvaluator()
    results = evaluator.run_benchmark(num_iterations=120)
    _benchmark_cache = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    return _benchmark_cache


@router.get("/api/stream")
async def stream_events(speed: float = 1.0):
    """
    Server-Sent Events stream — replays dataset rows in real-time.
    """
    _ensure_trained()

    async def event_generator():
        global _stream_active
        _stream_active = True
        try:
            for _, row in _df.iterrows():
                if not _stream_active:
                    break

                # Run anomaly detection
                event = _detector.predict_row(row)

                # Trigger AI pipeline if anomaly detected
                if event["anomaly"]:
                    # WINNER MOVE: Capture and stream agentic progress
                    progress_messages = []
                    def progress_cb(msg):
                        progress_messages.append(msg)

                    event = await asyncio.get_event_loop().run_in_executor(
                        None, trigger_agent_pipeline, event, progress_cb
                    )
                    
                    # Yield progress messages before the final event
                    for msg in progress_messages:
                        yield {"event": "agent_status", "data": json.dumps({"message": msg})}

                    _record_incident(event)

                payload = json.dumps(event)
                yield {"event": "metric", "data": payload}

                delay = 0.5 / max(speed, 0.1)
                await asyncio.sleep(delay)
        finally:
            _stream_active = False

    return EventSourceResponse(event_generator())


@router.post("/api/stream/stop")
def stop_stream():
    global _stream_active
    _stream_active = False
    return {"status": "stopped"}


@router.post("/api/inject-anomaly")
def inject_anomaly():
    """
    Demo endpoint — injects a scripted high-severity anomaly into the pipeline.
    """
    _ensure_trained()
    import pandas as pd

    scripted_row = pd.Series({
        "timestamp": pd.Timestamp.now(),
        "latency_ms": 380.0,
        "throughput_mbps": 160.0,
        "packet_loss_pct": 22.0,
        "jitter_ms": 65.0,
        "connections": 950,
    })

    event = _detector.predict_row(scripted_row)
    event["anomaly"] = True  
    event["severity"] = "high"
    event["primary_metric"] = "latency_ms"

    result = trigger_agent_pipeline(event)
    _record_incident(result)
    return result
