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
