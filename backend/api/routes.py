import asyncio
import json
import logging
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from backend.anomaly.preprocess import load_dataset
from backend.anomaly.detector import AnomalyDetector
from backend.events.trigger import trigger_agent_pipeline
from backend.data_factory import industrialDataFactory

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Shared state ---
DATA_PATH = Path(__file__).parent.parent.parent / "data" / "industrial_network_live.csv"
_df = None
_detector = AnomalyDetector()
_stream_active = False


def _ensure_trained():
    global _df, _detector
    if _df is None:
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
    return {"status": "ok", "model": "IsolationForest", "ai": "Gemma (Ollama)"}


@router.get("/api/metrics/history")
def metrics_history():
    """Return the full dataset for initial chart rendering."""
    _ensure_trained()
    # Take last 100 points for initial UI load
    records = _df.tail(100).to_dict(orient="records")
    for r in records:
        r["timestamp"] = str(r["timestamp"])
    return {"data": records}


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

                payload = json.dumps(event)
                yield {"event": "metric", "data": payload}

                await asyncio.sleep(0.5 * speed)
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
    return result
