# NetGuardian Runbook

## Start Locally
1. Install backend: `python -m pip install -e .[dev]`
2. Start backend: `uvicorn backend.main:app --reload`
3. Start frontend:
   - `cd frontend`
   - `npm ci`
   - `npm run dev`

## Required Environment
Set values from `.env.example`, especially:
- `NETGUARDIAN_API_TOKEN`
- `OLLAMA_URL`
- `OLLAMA_MODEL`

## Health Checks
- API root: `/`
- Liveness/readiness: `/api/health`, `/ready`
- Metrics: `/metrics`

## Incident Operations
- Acknowledge: `POST /api/incidents/{incident_id}/ack`
- Resolve: `POST /api/incidents/{incident_id}/resolve`

