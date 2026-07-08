# Claude Guidance — Agentic Invoice Processing

A single-user, monorepo invoice-processing tool that reworks the legacy
multi-service pipeline into one **Strands Agents** flow behind a chat API, with a
React UI. Two folders: **`backend/`** (Python 3.11+, FastAPI, SQLAlchemy 2.0 +
**PostgreSQL** via **Alembic**, connection from `DATABASE_URL`) and
**`frontend/`** (React + Vite, calls the non-streaming `POST /chat`, CORS enabled).
No email service, no auth. There is no SSE streaming endpoint. `specs/` holds the
Spec-Kit artifacts. All backend paths below are under `backend/`.

Core shape: one **Orchestrator agent** (OpenAI model) with five tools —
`extract_document` (Gemini vision, structured output), `lookup_purchase_order`
(DB read), `store_purchase_order` + `store_decision` (DB write), and `calculate`
(deterministic math). Validation and invoice↔PO reconciliation are done by the
orchestrator's reasoning, not as tools. A PO is resolved from an uploaded document
(extract → upsert) or by lookup on the invoice's PO number; reconciliation is
skipped when neither resolves. Results persist to `processed_invoices`; PO
reference tables are seeded from the project CSVs and only ever upserted (never
deleted). Raw upload bytes never outlive the request.

Layering (Reusable-Core-First): pure logic in `backend/app/db/` and
`backend/app/services/`, Strands wrappers in `backend/app/agent/tools/`, agent
composition in `backend/app/agent/orchestrator.py`, thin handlers in
`backend/app/api/`. All prompt text lives in one place —
`backend/app/agent/prompts.py` (orchestrator system prompt + invoice/PO extraction
prompts as named constants); no inline prompt strings elsewhere. Prefer functional
patterns; the only classes are framework-mandated (Pydantic, SQLAlchemy ORM, the
Strands `Agent`). Secrets (OpenAI/Gemini keys, `DATABASE_URL`) come from the
environment / a gitignored `backend/.env` — never commit them or the `*.db` file.

Validation (run from `backend/`): `alembic upgrade head` (creates the 4 tables),
`python -c "import app.main"` (import check), `uvicorn app.main:app` + `GET /health`,
and `pytest --cov=app`. Tests stub the model providers and inject a deterministic
fake agent via the `AGENT_FACTORY` seam; the DB schema is built on in-memory SQLite
via portable ORM types (or a real Postgres via `TEST_DATABASE_URL`).

<!-- SPECKIT START -->
Active feature plan (this branch): `specs/002-read-reporting/plan.md` — a READ-ONLY
reporting surface over 001's data: six GET endpoints (`/invoices`, `/invoices/{id}`,
`/summary`, `/purchase-orders(/{no})`, `/vendors`) in a new `backend/app/api/reports.py`
(+ `services/reporting_service.py` pure logic + `db/read_repository.py`), and React
screens (history list, invoice detail, dashboard w/ aging+priority, PO/vendor browsers)
behind a `react-router-dom` nav shell. No new tables/migration, no writes (SEC-002),
no raw-file viewer (SEC-003); per-run grain; vendor/amount/aging/priority derived in
Python from the `extracted_invoice` JSON (R1). Read `research.md` + `data-model.md` +
`contracts/read-endpoints.md` before touching the read path.

Prior feature: `specs/001-agentic-invoice-strands/plan.md`.
Read the plan plus `research.md` (R1 single-agent-+-tools topology, R2 OpenAI/Gemini
provider split, R3 image-routing-to-the-extraction-tool, R5 per-conversation agent
registry are the cruxes), `data-model.md` (Pydantic domain schemas + the SQLite ORM
tables — PO reference tables are upsert-only, `processed_invoices` is the results
store), `contracts/` (chat-endpoint, health-endpoint, agent-tools), and
`quickstart.md` before touching `backend/app/agent/`, `backend/app/api/chat.py`,
`backend/app/services/`, `backend/app/db/`, or the tool set. The chat surface is a single multimodal `POST /chat`
(multi-turn, text + invoice/PO uploads) returning a natural-language reply plus a
structured `Decision`; `NEEDS_REVIEW` is a 200 outcome, `503` is reserved for
transient provider/DB failures.
<!-- SPECKIT END -->
