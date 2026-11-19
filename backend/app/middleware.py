"""Structured JSON logging + Prometheus metrics for the platform prototype."""

import time

import structlog
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

TOTAL_REQUESTS = {"count": 0}

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.BoundLogger,
)

logger = structlog.get_logger("http")

http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"],
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)
approvals_total = Counter(
    "approvals_total",
    "Approval decisions by resulting status",
    ["status"],
)
agent_runs_total = Counter(
    "agent_runs_total",
    "Number of agent runs",
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request: method, path, status, duration_ms, user (if authenticated)."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        status = str(response.status_code)
        TOTAL_REQUESTS["count"] += 1
        http_requests_total.labels(method=request.method, path=request.url.path, status=status).inc()
        http_request_duration_seconds.labels(method=request.method, path=request.url.path).observe(duration_ms / 1000)
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            user=getattr(request.state, "user", None),
        )
        return response
