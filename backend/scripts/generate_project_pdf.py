"""Generate a detailed PDF documentation of the AI-Powered Internal Platform Prototype."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path(__file__).resolve().parent.parent.parent / "docs" / "PROJECT_DOCUMENTATION.pdf"

styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="H1",
        parent=styles["Heading1"],
        fontSize=22,
        spaceAfter=12,
    )
)
styles.add(
    ParagraphStyle(
        name="H2",
        parent=styles["Heading2"],
        fontSize=15,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="H3",
        parent=styles["Heading3"],
        fontSize=12,
        spaceAfter=4,
    )
)
styles.add(ParagraphStyle(name="Body", parent=styles["Normal"], fontSize=10, leading=14))
styles.add(ParagraphStyle(name="Small", parent=styles["Body"], fontSize=8, leading=12, textColor=colors.gray))

flow = []


def add_heading(text: str):
    flow.append(Paragraph(text, styles["H1"]))
    flow.append(Spacer(1, 6))


def add_sub(text: str):
    flow.append(Paragraph(text, styles["H2"]))
    flow.append(Spacer(1, 4))


def add_subsub(text: str):
    flow.append(Paragraph(text, styles["H3"]))
    flow.append(Spacer(1, 2))


def add_body(text: str):
    flow.append(Paragraph(text, styles["Body"]))
    flow.append(Spacer(1, 6))


def add_bullets(items):
    for it in items:
        flow.append(Paragraph(f"\u2022 {it}", styles["Body"]))
    flow.append(Spacer(1, 6))


def add_table(headers, rows):
    data = [headers] + rows
    table = Table(data, colWidths=[2.2 * inch, 3.8 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    flow.append(table)
    flow.append(Spacer(1, 10))


# ---------------- Title page content ----------------
add_heading("AI-Powered Internal Platform Prototype")
add_body("A portfolio project for AI agent workflows with human oversight.")
add_body("Built for Apple-style 'Junior Fullstack Engineer' interview preparation.")

# ---------------- Overview ----------------
add_heading("1. Overview")
add_body(
    "The project is a small internal platform prototype where an LLM agent proposes "
    "operational actions (for example scheduling a study session, generating a quiz, or "
    "drafting a learning plan). Every proposed action enters an approval queue. A human "
    "admin reviews and approves or rejects it. Approved actions are executed (mocked in "
    "this prototype) and every decision is written to an audit trail. The whole system is "
    "instrumented with structured logs, Prometheus metrics, a Grafana dashboard, health and "
    "stats endpoints."
)
add_bullets(
    [
        "Full-stack: FastAPI backend + React/TypeScript frontend + database.",
        "Agentic workflow: LLM agent proposes -> human approves -> mocked execution.",
        "Safety: human-in-the-loop approval + immutable-ish audit trail.",
        "Observability: logs, metrics, dashboard, runbook.",
        "Security: JWT auth, roles, strict validation, graceful errors.",
        "Evaluation: mock agent accuracy over 20 sample instructions.",
    ]
)

# ---------------- What it does ----------------
add_heading("2. What It Does")
add_body("Step by step user/operator flow:")
add_bullets(
    [
        "User logs in (JWT, admin or viewer).",
        "User sends a natural-language instruction to the agent (max 500 chars).",
        "Agent returns 1-3 proposed tool calls; each becomes an ApprovalRequest with status PROPOSED.",
        "Human approves or rejects via the UI/API (admin only).",
        "On approve: status -> APPROVED -> mocked execution -> EXECUTED, audit event written.",
        "On reject: status -> REJECTED, audit event written.",
        "Metrics/logs/dashboard reflect behavior in real time.",
    ]
)

# ---------------- Why it matters ----------------
add_heading("3. Why It Matters")
add_body(
    "The project demonstrates the skills Apple seeks in a Junior Fullstack Engineer: full-stack "
    "features (data model, services, APIs, UI), agentic workflows with human oversight, security "
    "basics, and observability. It shows an end-to-end product thinking: agent behavior, safety, "
    "operations, and measurement."
)

# ---------------- Tech stack ----------------
add_heading("4. Tech Stack")
add_table(
    ["Layer", "Technology"],
    [
        ["Backend", "Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy, PostgreSQL/SQLite, JWT (python-jose), bcrypt, structlog, prometheus-client"],
        ["Frontend", "React 18, TypeScript, Vite, plain CSS, accessible UI"],
        ["Agent", "Mock agent (keyword-based tool proposals); real OpenAI tool-calling ready"],
        ["Observability", "structlog (JSON logs), prometheus-client (/metrics), Grafana dashboard JSON"],
        ["Testing", "pytest, httpx TestClient"],
        ["Evaluation", "Custom eval harness: 20 instructions, accuracy = correct/20"],
    ],
)

# ---------------- Architecture ----------------
add_heading("5. Architecture")
add_body("Three-component architecture:")
add_bullets(
    [
        "React UI -> FastAPI -> Database.",
        "FastAPI handles auth, agent, approvals, audit, metrics.",
        "Database stores User, Tool, ApprovalRequest, AuditEvent.",
    ]
)
add_sub("Approval state machine")
add_body("PROPOSED -> APPROVED -> EXECUTED   OR   PROPOSED -> REJECTED")
add_body("Why human oversight: agents can be confidently wrong; audit trails create accountability.")

# ---------------- API ----------------
add_heading("6. API Endpoints")
add_table(
    ["Method", "Path", "Purpose"],
    [
        ["GET", "/health", "Liveness + DB check"],
        ["POST", "/auth/register", "Create user (dev)"],
        ["POST", "/auth/login", "Login -> JWT"],
        ["POST", "/approvals/agent/run", "Agent proposes actions"],
        ["GET", "/approvals", "List approvals (filter by status)"],
        ["POST", "/approvals/{id}/approve", "Admin approves -> execute + audit"],
        ["POST", "/approvals/{id}/reject", "Admin rejects + audit"],
        ["GET", "/audit", "Audit trail"],
        ["GET", "/metrics", "Prometheus metrics"],
        ["GET", "/stats", "Simple summary for UI"],
    ],
)

# ---------------- Verification ----------------
add_heading("7. Verification and Results")
add_body("Backend test suite: 6 tests passed (health, auth, approvals, observability).")
add_body("Eval harness: 20/20 instructions correct = 100.00% agent accuracy (eval_results.json).")
add_body("Live checks passed: health, register/login, agent run, approve, audit, metrics, stats, viewer 403.")

# ---------------- How to run ----------------
add_heading("8. How to Run")
add_sub("Backend (from backend/)")
add_bullets(
    [
        "python -m venv .venv",
        "pip install -r requirements.txt",
        "cp .env.example .env",
        "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000",
    ]
)
add_sub("Frontend (from frontend/)")
add_bullets(["npm install", "npm run dev"])

# ---------------- Security ----------------
add_heading("9. Security Highlights")
add_bullets(
    [
        "JWT auth with admin/viewer roles; approve endpoints require admin (viewer gets 403).",
        "Strict Pydantic schemas: extra fields rejected, validated ranges, clean 4xx JSON errors.",
        "Passwords hashed; secrets via environment variables; .env.example committed.",
        "Least privilege: viewer is read-only.",
    ]
)

# ---------------- Learnings ----------------
add_heading("10. What I Learned / Interview Talking Points")
add_bullets(
    [
        "Full-stack delivery: backend, frontend, database, API integration.",
        "Agentic design: propose vs. execute, human-in-the-loop, auditability.",
        "Security: authn/authz, validation, graceful failure, least privilege.",
        "Observability: logs, metrics, latency, alerting, runbooks.",
        "Evaluation: quantitative agent performance (accuracy) for credible claims.",
        "Engineering process: design first, build step by step, test each step, measure.",
    ]
)

doc = SimpleDocTemplate(str(OUT), pagesize=A4, title="AI-Powered Internal Platform Prototype", author="AI Job Search Candidate")
doc.build(flow)

print(f"PDF written to {OUT}")
