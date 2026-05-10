"""NetGuardian — Offline AI Network Incident Response System
FastAPI application entrypoint.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.config import settings
from backend.observability import RequestContextMiddleware, get_metrics_snapshot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

app = FastAPI(
    title="NetGuardian API",
    description="Offline AI Network Incident Response System",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    from backend.db import init_db, add_knowledge_entry
    await init_db()
    # Seed a high-impact demo entry
    await add_knowledge_entry(
        name="Gemma-Induced Buffer Flush",
        description="Observed when high-frequency telemetry overloads the Core-DC edge. Characterized by latency spikes > 300ms.",
        remedy="Apply 75% traffic throttling to the affected ingress leaf and prioritize BGP control plane traffic.",
        incident_id="SEED-001"
    )

app.add_middleware(RequestContextMiddleware)

# Allow the React frontend (localhost:5173) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key", "X-Request-ID"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "name": "NetGuardian",
        "status": "online",
        "docs": "/docs",
        "stream": "/api/stream",
    }


@app.get("/ready")
def ready():
    return {"status": "ready", "environment": settings.environment}


@app.get("/metrics")
def metrics():
    return {"routes": get_metrics_snapshot()}
