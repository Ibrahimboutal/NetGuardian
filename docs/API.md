# API Contract (Summary)

## Core
- `GET /api/health`
- `GET /api/metrics/history`
- `GET /api/stream` (SSE)
- `POST /api/stream/stop`
- `POST /api/inject-anomaly`

## Incident Intelligence
- `GET /api/incidents/recent`
- `GET /api/incidents/insights`
- `GET /api/incidents/forecast`
- `GET /api/system/summary`
- `GET /api/evaluation/benchmark`

## Sensitive/Controlled
- `GET /api/incidents/export` (requires `X-API-Key`)
- `POST /api/incidents/{incident_id}/ack` (requires `X-API-Key`)
- `POST /api/incidents/{incident_id}/resolve` (requires `X-API-Key`)

## Headers
- `X-API-Key`: required for protected endpoints
- `X-Request-ID`: optional request correlation id

