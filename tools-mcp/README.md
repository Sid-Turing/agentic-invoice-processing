# tools-mcp — external MCP tools server

Hosts the agent's **DB-only tools** as a standalone MCP server (streamable-HTTP at
`/mcp`), so the agent can call them remotely. Tools:

- `calculate(expression)` — deterministic arithmetic (no DB)
- `lookup_purchase_order(po_number)` — read a PO + vendor + line items
- `store_purchase_order(purchase_order)` — upsert an uploaded PO

(`extract_document` and `store_decision` stay in the backend — they need request
state, not just the DB.)

Only dependency: **`DATABASE_URL`** (the same Postgres the backend uses).

## Run locally

```bash
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://invoice:invoice@localhost:5434/invoices
export PORT=9001
python server.py            # MCP at http://localhost:9001/mcp
```

Point the backend at it: `MCP_TOOLS_URL=http://localhost:9001/mcp` (unset → the
backend runs all tools in-process). Via docker-compose this is already wired
(`tools-mcp` service; backend `MCP_TOOLS_URL=http://tools-mcp:8080/mcp`).

## Deploy to GCP (Cloud Run)

Cloud Run fits MCP streamable-HTTP (a long-lived HTTP server); it listens on the
injected `$PORT`. Connect it to Cloud SQL (Postgres).

```bash
PROJECT=your-project REGION=us-central1
INSTANCE=$PROJECT:$REGION:invoices-pg        # your Cloud SQL instance connection name

gcloud run deploy invoice-tools-mcp \
  --source . \
  --project "$PROJECT" --region "$REGION" \
  --add-cloudsql-instances "$INSTANCE" \
  --set-env-vars "DATABASE_URL=postgresql+psycopg2://invoice:invoice@/invoices?host=/cloudsql/$INSTANCE" \
  --allow-unauthenticated
```

- Cloud SQL over the built-in socket → DSN host is `/cloudsql/<INSTANCE>` (no host/port).
- The deploy prints a service URL; the MCP endpoint is `https://<service-url>/mcp`.
  Set the backend's `MCP_TOOLS_URL` to that.
- **Auth**: `--allow-unauthenticated` is simplest for a demo. To lock it down, drop
  that flag and have the backend send a Cloud Run ID token (`Authorization: Bearer`)
  — the MCP client's `streamablehttp_client(url, headers=...)` accepts headers.
- Put DB credentials in **Secret Manager** (`--set-secrets DATABASE_URL=...:latest`)
  rather than plaintext env for anything beyond a demo.

## Notes

- Schema/seed data are owned by the backend's Alembic migrations; this server only
  reads/upserts the existing PO tables.
- `stateless_http=True` — each MCP call is independent, so it scales cleanly on
  Cloud Run (no session affinity needed).
