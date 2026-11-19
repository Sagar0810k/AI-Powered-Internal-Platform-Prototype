# DESIGN.md — AI-Powered Internal Platform Prototype

A small internal "learning system" style ops platform for Apple-level internal tooling: an LLM agent proposes learning / operational actions, a human approves them in the UI, and approved actions are executed (mocked) with a full audit trail.

## 1. Components (3-part architecture)

1. **React UI** (`frontend/`) — accessible, keyboard-friendly. Views: login, "Ask the agent", approval queue, audit trail, metrics summary.
2. **FastAPI backend** (`backend/app/`) — REST API, auth, agent orchestration, approval workflow, audit events, metrics.
3. **Database** (`backend/app/db`) — SQLAlchemy + PostgreSQL (SQLite via `DATABASE_URL` for local dev).

## 2. Data model

- `User(id, email, hashed_password, role)` — roles: `admin` (approve), `viewer` (read-only).
- `Tool(id, name, description, ...)` — the set of actions the agent can propose.
- `ApprovalRequest(id, agent_name, tool_name, tool_args JSON, status, created_at, decided_at, decided_by)` — status flow: `PROPOSED -> APPROVED/REJECTED -> EXECUTED`.
- `AuditEvent(id, request_id, action, actor, detail, timestamp)`.

## 3. Approval state machine

```
PROPOSED --(human approve)--> APPROVED --(mocked executor)--> EXECUTED
PROPOSED --(human reject)-->  REJECTED
```

No action executes before human approval. Every transition writes an `AuditEvent`.

## 4. Why human oversight matters

LLM agents can be confidently wrong (bad tool args, stale runbooks, harmful actions). An approval queue + audit trail gives accountability, lets humans review context, and keeps a human in the loop for consequential actions.

## 5. Security goals (later steps)

JWT auth, role-based access control (admin/viewer), strict Pydantic validation (reject extra fields, clean 4xx JSON errors, no stack traces), secrets via env vars, password hashing.

## 6. Observability goals (later steps)

Structured JSON logs (structlog), Prometheus metrics (`/metrics`), Grafana dashboard, `/health`.
