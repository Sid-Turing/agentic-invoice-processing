# Contract: `GET /health`

**Feature**: `001-agentic-invoice-strands` | Satisfies SCH-002, FR-025

Lightweight liveness/readiness probe. Confirms the service is up and reports
whether its model providers and database are reachable/configured.

## Request

`GET /health` — no parameters, no body.

## Response — `200 application/json` → `HealthResponse`

```json
{
  "status": "ok",
  "providers": { "openai": true, "gemini": true },
  "database": true
}
```

- `providers.<name>` = `true` when the corresponding API key is configured and the
  client initializes (a cheap check — not a live model round-trip).
- `database` = `true` when a trivial `SELECT 1` against the SQLite file succeeds.
- `status` = `"ok"` when the database is reachable and at least the OpenAI provider
  (orchestrator) is configured; otherwise `"degraded"`.

## Status codes

| Code | When |
|---|---|
| `200` | Always returned when the process is alive; `status` conveys readiness. |

The endpoint never returns 5xx for a configuration gap — it reports `degraded` so
`VAL-001` (startup check) can assert readiness explicitly.
