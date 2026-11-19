import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"


def call(method: str, path: str, body=None, token: str = None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read()
        return e.code, json.loads(raw) if raw else {}


status, body = call("POST", "/auth/login", {"email": "admin@example.com", "password": "demo1234"})
token = body.get("access_token") if isinstance(body, dict) else None
print("LOGIN", status, "token?", bool(token))

status, body = call(
    "POST",
    "/approvals/agent/run",
    {"agent_name": "mock-agent-v1", "instruction": "schedule a study session for sql joins"},
    token=token,
)
print("AGENT_RUN", status, body)
approval_id = body[0]["approval_id"]

status, body = call("GET", "/approvals", token=token)
print("LIST", status, body)

status, body = call(
    "POST",
    f"/approvals/{approval_id}/approve",
    {"decided_by": "admin@example.com"},
    token=token,
)
print("APPROVE", status, body)

status, body = call("GET", "/audit", token=token)
print("AUDIT", status, body)

status, body = call(
    "POST",
    "/approvals/agent/run",
    {"agent_name": "mock-agent-v1", "instruction": "generate a quiz for python"},
    token=token,
)
second_id = body[0]["approval_id"]
status, body = call(
    "POST",
    f"/approvals/{second_id}/reject",
    {"decided_by": "admin@example.com"},
    token=token,
)
print("REJECT", status, body)
