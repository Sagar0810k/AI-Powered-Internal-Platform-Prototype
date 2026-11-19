import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_auth_flow_register_and_login():
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    with TestClient(app) as client:
        register = client.post("/auth/register", json={"email": email, "password": "demo1234"})
        assert register.status_code == 200
        assert register.json()["role"] == "viewer"

        login = client.post("/auth/login", json={"email": email, "password": "demo1234"})
        assert login.status_code == 200
        body = login.json()
        assert body["token_type"] == "bearer"
        assert isinstance(body["access_token"], str) and body["access_token"]


def test_auth_register_rejects_extra_fields():
    with TestClient(app) as client:
        response = client.post(
            "/auth/register",
            json={"email": "hacker@example.com", "password": "demo1234", "role": "admin"},
        )
    # Strict Pydantic: extra="forbid" -> clean 422, never a stack trace
    assert response.status_code == 422
