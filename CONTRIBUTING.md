# Contributing to NetGuardian

## Development setup
1. Install backend deps: `python -m pip install -e .[dev]`
2. Install frontend deps: `cd frontend && npm ci`

## Before opening a PR
- Run backend tests: `pytest -q`
- Run frontend checks:
  - `npm run lint`
  - `npm run build`
  - `npm run test`

## Guidelines
- Keep changes focused and small.
- Add or update tests for behavior changes.
- Do not commit secrets; use `.env`/secret managers.
- Document new endpoints and operational changes in `docs/`.

