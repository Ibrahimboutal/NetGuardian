# Troubleshooting

## Backend does not start
- Confirm Python 3.10+.
- Run `python -m pip install -e .[dev]`.
- Verify `.env` values and file paths under `data/`.

## Frontend cannot connect
- Confirm backend running on `VITE_API_URL`.
- Check CORS origins with `NETGUARDIAN_CORS_ORIGINS`.

## Model responses missing
- Verify Ollama service and `OLLAMA_URL`.
- System falls back to deterministic responses if model is unavailable.

## Export/ack/resolve unauthorized
- Provide valid `X-API-Key` matching `NETGUARDIAN_API_TOKEN`.

## Stream disconnect loops
- Dashboard retries automatically every 3 seconds.
- Check backend logs and `/api/health`.

