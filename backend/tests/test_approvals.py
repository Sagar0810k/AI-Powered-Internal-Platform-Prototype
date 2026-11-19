import uuid

from fastapi.testclient import TestClient

from app import models, security
from app.database import SessionLocal
from app.main import app


def _make_admin_and_login(client: TestClient) -> str:
    email = "admin@example.com"
    db = SessionLocal()
    admin = db.query(models.User).filter(models.User.email == email).first()
    if admin is None:
        admin = models.User(email=email, hashed_password=security.hash_password("demo1234"), role="admin")
        db.add(admin)
        db.commit()
    db.close()

    login = client.post("/auth/login", json={"email": email, "password": "demo1234"})
    assert login.status_code == 200
    return login.json()["access_token"]


def test_agent_run_proposes_then_admin_approve_executes_and_audits():
    with TestClient(app) as client:
        token = _make_admin_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        run = client.post(
            "/approvals/agent/run",
            json={"agent_name": "mock-agent-v1", "instruction": "schedule a study session for sql joins"},
            headers=headers,
        )
        assert run.status_code == 200
        proposals = run.json()
        assert isinstance(proposals, list) and len(proposals) >= 1
        assert "approval_id" in proposals[0]
        assert "tool_name" in proposals[0]

        approval_id = proposals[0]["approval_id"]

        listing = client.get("/approvals", headers=headers)
        assert listing.status_code == 200
        assert any(item["id"] == approval_id for item in listing.json())

        decision = client.post(
            f"/approvals/{approval_id}/approve",
            json={"decided_by": "admin@example.com"},
            headers=headers,
        )
        assert decision.status_code == 200
        assert decision.json()["status"] == "EXECUTED"

        audit = client.get("/audit", headers=headers)
        assert audit.status_code == 200
        assert any(e["action"] == "approve" and e["request_id"] == approval_id for e in audit.json())


def test_viewer_cannot_approve():
    with TestClient(app) as client:
        email = f"viewer_{uuid.uuid4().hex[:6]}@example.com"
        reg = client.post("/auth/register", json={"email": email, "password": "demo1234"})
        assert reg.status_code == 200
        login = client.post("/auth/login", json={"email": email, "password": "demo1234"})
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        run = client.post(
            "/approvals/agent/run",
            json={"agent_name": "mock-agent-v1", "instruction": "generate a quiz for python"},
            headers=headers,
        )
        assert run.status_code == 200
        approval_id = run.json()[0]["approval_id"]

        decision = client.post(
            f"/approvals/{approval_id}/approve",
            json={"decided_by": email},
            headers=headers,
        )
        assert decision.status_code == 403
