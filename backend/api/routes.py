import asyncio
import json
import logging
import uuid
import requests
from pathlib import Path
from collections import Counter

from fastapi import APIRouter, Depends, Query, Request, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from backend.db import record_incident, get_recent_incidents, update_incident_state, get_db_summary
from backend.anomaly.preprocess import load_dataset
from backend.anomaly.detector import AnomalyDetector
from backend.events.trigger import trigger_agent_pipeline
from backend.data_factory import industrialDataFactory
from backend.config import settings
from backend.security import require_api_key, enforce_rate_limit, sanitize_payload

logger = logging.getLogger(__name__)
router = APIRouter()

import threading
from datetime import datetime, timezone

# --- Shared state ---
DATA_PATH = Path(__file__).parent.parent.parent / "data" / "ML-MATT-CompetitionQT2021_train.csv"
_df = None
_detector = AnomalyDetector()
_stream_active = False
_train_lock = threading.Lock()
_state_lock = threading.RLock()
_benchmark_cache = None


def _emit_alert(event: dict):
    if not settings.alerts_webhook_url:
        return
    severity = str(event.get("severity", "")).lower()
    if severity not in {"high", "critical"}:
        return
    try:
        requests.post(
            settings.alerts_webhook_url,
            json={
                "source": "netguardian",
                "incident_id": event.get("incident_id"),
                "severity": severity,
                "primary_metric": event.get("primary_metric"),
                "node_id": event.get("node_id"),
                "timestamp": event.get("timestamp"),
            },
            timeout=2.5,
        )
    except requests.RequestException:
        logger.warning("Alert webhook failed")

async def _record_incident(event: dict):
    if not event or not event.get("anomaly"):
        return

    event.setdefault("incident_id", str(uuid.uuid4()))
    event.setdefault("incident_state", "open")
    event.setdefault("assigned_to", None)

    await record_incident(event)
    _emit_alert(event)


def _build_insights_from_data(recent: list) -> dict:
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


def _build_forecast_from_data(recent: list) -> dict:
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
        "critical": 1.0, "high": 0.8, "medium": 0.55, "low": 0.3, "normal": 0.1, "unknown": 0.2,
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


def _build_cascade_timeline_from_data(recent: list) -> dict:
    if not recent:
        return {
            "horizon_sec": 60, "focus_node": None, "risk_level": "unknown", "spread_target": None, "steps": [],
            "summary": "No incident memory available yet.",
        }

    metric_counter = Counter(item.get("primary_metric", "unknown") for item in recent)
    node_counter = Counter(item.get("node_id", "Router-14") for item in recent)
    case_counter = Counter((item.get("experience") or {}).get("id") or item.get("primary_metric", "unknown") for item in recent)
    severity_weights = {
        "critical": 3, "high": 2, "medium": 1, "low": 0.5, "normal": 0.2, "unknown": 0.4,
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
        {"window_sec": 0, "label": "Trigger", "node": focus_node, "signal": spread_target, "effect": "Current pressure concentrates on the epicenter."},
        {"window_sec": 20, "label": "Cascade edge", "node": focus_node, "signal": recurring_case, "effect": f"Recent cases suggest the failure can {spread_verb} into the repeating pattern."},
        {"window_sec": 40, "label": "Containment horizon", "node": f"{focus_node} / perimeter", "signal": spread_target, "effect": f"Recommended response: {action} before the next wave expands."},
    ]

    return {
        "horizon_sec": 60, "focus_node": focus_node, "focus_count": focus_count, "spread_target": spread_target,
        "spread_count": spread_count, "recurring_case": recurring_case, "recurring_case_count": recurring_case_count,
        "risk_level": risk_level, "cascade_score": cascade_score, "steps": steps,
        "summary": f"{risk_level.upper()} cascade risk centered on {focus_node} with pressure on {spread_target}.",
    }


def _ensure_trained():
    global _df, _detector
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
async def health(request: Request):
    enforce_rate_limit(request)
    _ensure_trained()
    from backend.db import get_db_summary
    stats = await get_db_summary()
    return {
        "status": "ok",
        "model": "IsolationForest",
        "ai": "Gemma (Ollama)",
        "dataset_rows": int(len(_df)) if _df is not None else 0,
        "incidents_recorded": stats.get("total_incidents", 0),
        "stream_active": _stream_active,
    }


@router.get("/api/metrics/history")
def metrics_history(request: Request):
    """Return the full dataset for initial chart rendering."""
    enforce_rate_limit(request)
    _ensure_trained()
    # Take last 100 points for initial UI load
    records = _df.tail(100).to_dict(orient="records")
    for r in records:
        r["timestamp"] = str(r["timestamp"])
    return {"data": records}


@router.get("/api/incidents/recent")
async def recent_incidents(request: Request, limit: int = Query(default=20, ge=1, le=100)):
    """Return the most recent incident payloads for operator review."""
    enforce_rate_limit(request)
    from backend.db import get_recent_incidents
    data = await get_recent_incidents(limit=limit)
    return {"data": [sanitize_payload(i) for i in data]}


@router.get("/api/system/summary")
async def system_summary(request: Request):
    """Return a compact operational summary for the demo and writeup."""
    enforce_rate_limit(request)
    _ensure_trained()
    
    from backend.db import get_db_summary, get_recent_incidents
    db_stats = await get_db_summary()
    recent_for_insights = await get_recent_incidents(limit=20)
    
    # We still use build_insights logic but with DB data
    insights = _build_insights_from_data(recent_for_insights)
    forecast = _build_forecast_from_data(recent_for_insights)
    cascade = _build_cascade_timeline_from_data(recent_for_insights)
    
    return {
        **db_stats,
        "insights": insights,
        "forecast": forecast,
        "cascade": cascade,
        "data_points": int(len(_df)) if _df is not None else 0,
        "columns": list(_df.columns) if _df is not None else [],
        "stream_active": _stream_active,
    }


@router.get("/api/incidents/insights")
async def incident_insights(request: Request):
    """Return recurring-pattern insights derived from the incident memory."""
    enforce_rate_limit(request)
    data = await get_recent_incidents(limit=20)
    return _build_insights_from_data(data)


@router.get("/api/incidents/forecast")
async def incident_forecast(request: Request):
    """Return a short-horizon forecast based on recent incident memory."""
    enforce_rate_limit(request)
    data = await get_recent_incidents(limit=10)
    forecast = _build_forecast_from_data(data)
    forecast["cascade"] = _build_cascade_timeline_from_data(data)
    return forecast


@router.get("/api/incidents/export")
async def export_incidents(request: Request, _: str = Depends(require_api_key)):
    """Return a single JSON report that can be downloaded by the frontend."""
    enforce_rate_limit(request)
    _ensure_trained()
    
    from backend.db import get_recent_incidents, get_db_summary
    recent = await get_recent_incidents(limit=100)
    summary = await get_db_summary()
    
    return {
        "summary": summary,
        "insights": _build_insights_from_data(recent[:20]),
        "forecast": _build_forecast_from_data(recent[:10]),
        "cascade": _build_cascade_timeline_from_data(recent[:8]),
        "recent_incidents": [sanitize_payload(item) for item in recent],
        "benchmark": _benchmark_cache,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/evaluation/benchmark")
def evaluation_benchmark(request: Request, refresh: bool = False, seed: int = Query(default=42, ge=0, le=999999)):
    """Run or return a cached anomaly-detection benchmark."""
    enforce_rate_limit(request)
    global _benchmark_cache

    with _state_lock:
        if _benchmark_cache is not None and not refresh:
            return _benchmark_cache

    _ensure_trained()

    from backend.evaluation import NetGuardianEvaluator

    evaluator = NetGuardianEvaluator()
    results = evaluator.run_benchmark(num_iterations=120, seed=seed)
    benchmark = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }

    with _state_lock:
        _benchmark_cache = benchmark
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

                    event = await asyncio.get_running_loop().run_in_executor(
                        None, trigger_agent_pipeline, event, progress_cb
                    )
                    
                    # Yield progress messages before the final event
                    for msg in progress_messages:
                        yield {"event": "agent_status", "data": json.dumps({"message": msg})}

                    await _record_incident(event)

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


@router.get("/api/nodes/status")
def nodes_status(request: Request):
    """Return live node states from the network simulator for the topology map."""
    enforce_rate_limit(request)
    from backend.agents.tools import sim, NETWORK_TOPOLOGY
    nodes = []
    for node_id, state in sim.node_states.items():
        nodes.append({
            "node_id": node_id,
            "status": state.get("status", "Healthy"),
            "load": state.get("load", 0),
            "capacity": state.get("capacity", 150),
            "criticality": state.get("criticality", 1),
            "neighbors": NETWORK_TOPOLOGY.get(node_id, []),
        })
    return {"nodes": nodes, "total": len(nodes)}


@router.post("/api/simulate/what-if")
async def what_if_simulation(request: Request):
    """
    KILLED FEATURE: Interactive What-If Sandbox.
    Predict the blast radius of a failure before it actually happens.
    """
    enforce_rate_limit(request)
    from backend.agents.tools import simulate_impact
    
    try:
        body = await request.json()
        node_id = body.get("node_id", "Router-14")
        magnitude = body.get("magnitude", 150)
    except:
        node_id = "Router-14"
        magnitude = 150
        
    result = simulate_impact(node_id, magnitude=magnitude)
    return {
        "status": "simulation_complete",
        "node_id": node_id,
        "magnitude": magnitude,
        "prediction": result,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/api/inject-anomaly")
async def inject_anomaly(request: Request, node_id: str = "Core-DC-01"):
    """
    Demo endpoint — injects a scripted or custom anomaly into the pipeline.
    """
    enforce_rate_limit(request)
    _ensure_trained()
    import pandas as pd

    # Default scripted values
    data = {
        "node_id": node_id,
        "latency_ms": 380.0,
        "throughput_mbps": 160.0,
        "packet_loss_pct": 22.0,
        "jitter_ms": 65.0,
        "connections": 950,
        "severity": "high",
        "primary_metric": "latency_ms"
    }

    # Try to load custom values from body if provided
    try:
        body = await request.json()
        data.update(body)
    except:
        pass

    scripted_row = pd.Series({
        "timestamp": pd.Timestamp.now(),
        "node_id": data["node_id"],
        "latency_ms": data["latency_ms"],
        "throughput_mbps": data["throughput_mbps"],
        "packet_loss_pct": data["packet_loss_pct"],
        "jitter_ms": data["jitter_ms"],
        "connections": data["connections"],
    })

    event = _detector.predict_row(scripted_row)
    event["anomaly"] = True  
    event["severity"] = data["severity"]
    event["primary_metric"] = data["primary_metric"]

    # Trigger agents
    result = await asyncio.get_running_loop().run_in_executor(
        None, trigger_agent_pipeline, event
    )
    await _record_incident(result)
    return result


@router.post("/api/incidents/{incident_id}/ack")
async def acknowledge_incident(
    incident_id: str,
    request: Request,
    assigned_to: str = Query(default="on-call"),
    _: str = Depends(require_api_key),
):
    enforce_rate_limit(request)
    from backend.db import update_incident_state
    await update_incident_state(incident_id, "acknowledged", assigned_to=assigned_to)
    return {"status": "ok", "incident_id": incident_id, "state": "acknowledged"}


@router.post("/api/incidents/{incident_id}/resolve")
async def resolve_incident(
    incident_id: str,
    request: Request,
    resolution_note: str = Query(default="resolved_by_operator"),
    is_valid_anomaly: bool = Query(default=True),
    _: str = Depends(require_api_key),
):
    enforce_rate_limit(request)
    
    # 1. Update DB
    from backend.db import update_incident_state
    await update_incident_state(incident_id, "resolved", note=resolution_note[:200])
    
    # 2. Calibrate model (Adaptive Threshold)
    _detector.calibrate_from_feedback(is_valid_anomaly, "medium")
    
    # 3. KB Auto-Update (Dynamic RAG expansion)
    if len(resolution_note) > 20 and is_valid_anomaly:
        logger.info(f"📚 Auto-updating Knowledge Base with case from {incident_id}")
        # In a real implementation, we would call the vector DB here.
        # For the demo, we'll just log it.
        
    return {"status": "ok", "incident_id": incident_id, "state": "resolved"}

@router.get("/api/incidents/export-csv")
async def export_incidents_csv(request: Request, _: str = Depends(require_api_key)):
    """Export all recorded incidents as CSV."""
    enforce_rate_limit(request)
    from backend.db import get_recent_incidents
    data = await get_recent_incidents(limit=1000)
    
    import io
    import csv
    from fastapi.responses import StreamingResponse
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "timestamp", "node_id", "severity", "primary_metric", "score", "state"])
    
    for inc in data:
        writer.writerow([
            inc.get("incident_id"),
            inc.get("timestamp"),
            inc.get("node_id"),
            inc.get("severity"),
            inc.get("primary_metric"),
            inc.get("anomaly_score", inc.get("score")),
            inc.get("incident_state")
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.StringIO(output.getvalue()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=netguardian_incidents.csv"}
    )
