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


status, body = call("GET", "/health")
print("HEALTH", status, body)

status, body = call("POST", "/auth/register", {"email": "sagar@example.com", "password": "demo1234"})
print("REGISTER", status, body)

status, body = call("POST", "/auth/login", {"email": "sagar@example.com", "password": "demo1234"})
print("LOGIN", status, body)
token = body.get("access_token") if isinstance(body, dict) else None
if token:
    status, body = call("GET", "/health", token=token)
    print("HEALTH_AUTHED", status, body)

status, body = call("POST", "/auth/register", {"email": "bad", "password": "demo1234", "role": "admin"})
print("REGISTER_STRICT", status, body)
