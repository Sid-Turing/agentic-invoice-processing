# Claude Guidance — Agentic Invoice Processing

A standalone, single-user backend service that reworks the legacy multi-service
invoice pipeline into one **Strands Agents** flow behind a ChatGPT-style
multimodal chat API. Python 3.11+, FastAPI, SQLAlchemy 2.0 + **PostgreSQL**
(schema created from scratch via **Alembic**; connection from `DATABASE_URL`,
swappable). No email service, no auth. **Backend API only** — the web UI is a
separate React (Vite) repo `agentic-invoice-frontend` that calls the non-streaming
`POST /chat` (CORS enabled). There is no built-in UI and no SSE streaming endpoint.

Core shape: one **Orchestrator agent** (OpenAI model) with five tools —
`extract_document` (Gemini vision, structured output), `lookup_purchase_order`
(DB read), `store_purchase_order` + `store_decision` (DB write), and `calculate`
(deterministic math). Validation and invoice↔PO reconciliation are done by the
orchestrator's reasoning, not as tools. A PO is resolved from an uploaded document
(extract → upsert) or by lookup on the invoice's PO number; reconciliation is
skipped when neither resolves. Results persist to `processed_invoices`; PO
reference tables are seeded from the project CSVs and only ever upserted (never
deleted). Raw upload bytes never outlive the request.

Layering (Reusable-Core-First): pure logic in `app/db/` and `app/services/`,
Strands wrappers in `app/agent/tools/`, agent composition in
`app/agent/orchestrator.py`, thin handlers in `app/api/`. All prompt text lives in
one place — `app/agent/prompts.py` (orchestrator system prompt + invoice/PO
extraction prompts as named constants); no inline prompt strings elsewhere. Prefer functional
patterns; the only classes are framework-mandated (Pydantic, SQLAlchemy ORM, the
Strands `Agent`). Secrets (OpenAI/Gemini keys, `DATABASE_URL`) come from the
environment / a gitignored `.env` — never commit them or the `*.db` file.

Validation: `alembic upgrade head` (creates the 4 tables), `python -c "import
app.main"` (import check), `uvicorn app.main:app` + `GET /health`, and
`pytest --cov=app`. Tests stub the model providers and inject a deterministic fake
agent via the `AGENT_FACTORY` seam; the DB schema is built on in-memory SQLite via
portable ORM types (or a real Postgres via `TEST_DATABASE_URL`).

<!-- SPECKIT START -->
Active feature plan (this branch): `specs/001-agentic-invoice-strands/plan.md`.
Read the plan plus `research.md` (R1 single-agent-+-tools topology, R2 OpenAI/Gemini
provider split, R3 image-routing-to-the-extraction-tool, R5 per-conversation agent
registry are the cruxes), `data-model.md` (Pydantic domain schemas + the SQLite ORM
tables — PO reference tables are upsert-only, `processed_invoices` is the results
store), `contracts/` (chat-endpoint, health-endpoint, agent-tools), and
`quickstart.md` before touching `app/agent/`, `app/api/chat.py`, `app/services/`,
`app/db/`, or the tool set. The chat surface is a single multimodal `POST /chat`
(multi-turn, text + invoice/PO uploads) returning a natural-language reply plus a
structured `Decision`; `NEEDS_REVIEW` is a 200 outcome, `503` is reserved for
transient provider/DB failures.
<!-- SPECKIT END -->
