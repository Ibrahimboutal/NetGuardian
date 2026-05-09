"""NetGuardian — Offline AI Network Incident Response System
FastAPI application entrypoint.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

app = FastAPI(
    title="NetGuardian API",
    description="Offline AI Network Incident Response System",
    version="1.0.0",
)

# Allow the React frontend (localhost:5173) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
