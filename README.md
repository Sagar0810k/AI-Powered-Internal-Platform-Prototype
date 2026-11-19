# AI-Powered Internal Platform Prototype

A portfolio project for Apple-style "Junior Fullstack Engineer" interviews: an LLM agent proposes operational actions inside an **approval queue** with human oversight, audit trail, security, and observability.

## What it does

1. **Agent**: accepts a natural-language instruction (max 500 chars) and proposes 1–3 tool calls (e.g. schedule a study session, generate a quiz, draft a learning plan).
2. **Approval workflow**: every proposal lands in a queue as `PROPOSED`. An **admin** approves or rejects. On approve → mocked execution → `EXECUTED` + audit event. On reject → `REJECTED` + audit event. **No action executes before human approval.**
3. **Audit trail**: every decision is recorded (`AuditEvent`: request, action, actor, detail, timestamp).
4. **Observability**: JSON logs (structlog), Prometheus metrics (`/metrics`), Grafana dashboard (`grafana/dashboard.json`), `/health`, `/stats`, runbook (`docs/RUNBOOK.md`).
5. **Security**: JWT auth (admin/viewer), strict Pydantic validation (reject extra fields), password hashing, env-based secrets, graceful 4xx errors.
6. **Evaluation**: mock agent accuracy over 20 sample instructions → `eval.py` / `eval_results.json`.

## Tech stack

- Backend: Python 3.11+ / FastAPI, Pydantic v2, SQLAlchemy, PostgreSQL (SQLite via `DATABASE_URL`)
- Frontend: React 18 + TypeScript + Vite, plain CSS, accessible UI
- Observability: structlog, prometheus-client, Grafana dashboard JSON

## Project structure

```
AI-Powered-Internal-Platform-Prototype/
├── DESIGN.md
├── backend/
│   ├── app/            # FastAPI app
│   │   ├── api/        # auth, health, approvals, metrics
│   │   ├── agent.py   # mock LLM agent + executor
│   │   ├── middleware.py # structlog + prometheus + request logging
│   │   ├── models.py, schemas.py, security.py, database.py, config.py
│   ├── tests/          # pytest suite
│   ├── eval.py, eval_results.json
│   └── requirements.txt, .env.example
├── frontend/           # React + TS + Vite (accessible UI)
├── grafana/dashboard.json
└── docs/RUNBOOK.md
```

## Run it locally

Backend (from `backend/`):

```bash
python -m venv .venv
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend (from `frontend/`):

```bash
npm install
npm run dev        # http://localhost:5173 -> proxies /api calls to :8000
```

Demo login: **admin@example.com / demo1234** (admin can approve; viewer accounts are read-only and created via `POST /auth/register`).

### Demo flow

1. Login as admin.
2. `POST /approvals/agent/run` with an instruction → get proposal(s) (`PROPOSED`).
3. `POST /approvals/{id}/approve` → status becomes `EXECUTED` + audit event.
4. `GET /audit` → audit trail entries.

## API highlights

- `GET /health` — liveness + DB check
- `POST /auth/register`, `POST /auth/login` → JWT
- `POST /approvals/agent/run` — agent proposes
- `GET /approvals?status=PROPOSED` — queue
- `POST /approvals/{id}/approve`, `POST /approvals/{id}/reject` — admin only
- `GET /audit` — audit trail
- `GET /metrics` — Prometheus
- `GET /stats` — simple summary for UI

## Tests

```bash
cd backend && python -m pytest -q
```

## Eval

```bash
cd backend && python eval.py
# Agent accuracy: 20/20 = 100.00%
```

## Observability

- Logs: JSON via structlog (`method`, `path`, `status`, `duration_ms`, `user`)
- Metrics: `http_requests_total`, `http_request_duration_seconds`, `approvals_total{status}`, `agent_runs_total` at `/metrics`
- Grafana dashboard: `grafana/dashboard.json` (3 panels + error-rate alert >5%)

## Security notes

- JWT roles (`admin`, `viewer`); approve endpoints require admin (403 otherwise).
- Strict Pydantic schemas; extra fields rejected; clean 4xx JSON errors (no stack traces).
- Passwords hashed (bcrypt); secrets via env vars (`backend/.env.example`).
