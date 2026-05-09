# NetGuardian Architecture

## High-Level Flow
1. Telemetry stream or generated dataset enters backend.
2. Feature engine builds temporal feature vectors.
3. IsolationForest scores events and flags anomalies.
4. Agent pipeline simulates impact and proposes mitigation.
5. Frontend renders metrics, incident feed, and reasoning output.

## Core Components
- `backend/anomaly/*`: preprocessing + anomaly detection
- `backend/events/trigger.py`: orchestration and safety checks
- `backend/agents/*`: diagnosis/recommendation/explanation and tool interface
- `backend/api/routes.py`: API + SSE + incident memory/exports
- `frontend/src/components/*`: dashboard and operational widgets

## Security/Resilience Controls
- API key protection on sensitive endpoints
- In-memory rate limiting
- Sanitized exports/log persistence
- Incident retention and log rotation

