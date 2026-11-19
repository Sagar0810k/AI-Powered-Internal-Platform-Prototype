# RUNBOOK - Diagnose a Latency Spike

Symptom: p95 latency on `/health`, `/auth/*`, or agent endpoints is high; alerts firing.

## Steps

1. **Check the dashboard** (`/metrics` + Grafana): look at the "HTTP Request Latency (p95)" panel. Is p95 > 1s?

2. **Query Prometheus** for evidence:
   - `sum(rate(http_requests_total[5m]))` — traffic volume.
   - `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` — p95.
   - `sum(rate(http_requests_total{status=~"5..|4.."}[5m])) / sum(rate(http_requests_total[5m]))` — error rate.

3. **Read structured logs** (JSON via structlog) for the slow paths:
   - Look for `http_request` events with high `duration_ms`.
   - Correlate `path` + `status_code`.

4. **Check DB**: if latency is DB-bound, inspect slow queries (SQLite/Postgres).

5. **Mitigate**: rate-limit, scale horizontally, or roll back. Then resolve alert.

## Notes

- Metrics: `http_requests_total`, `http_request_duration_seconds`, `approvals_total{status}`, `agent_runs_total` at `/metrics`.
- Logs: JSON via structlog (`method`, `path`, `status`, `duration_ms`, `user`).
