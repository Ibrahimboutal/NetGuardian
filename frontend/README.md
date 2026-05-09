# NetGuardian Frontend

React/Vite operations dashboard for NetGuardian.

## Prerequisites
- Node.js 20+
- Backend API running (default `http://127.0.0.1:8000`)

## Configuration
Create `.env` in this folder:

```bash
VITE_API_URL=http://127.0.0.1:8000
```

## Commands
- `npm ci` — install dependencies
- `npm run dev` — start local dev server
- `npm run lint` — run ESLint
- `npm run build` — build production bundle
- `npm run test` — run component tests (Vitest)

## Notes
- The dashboard reconnects automatically when SSE stream connectivity is lost.
- Export endpoints may require `X-API-Key` if backend auth is enabled.

