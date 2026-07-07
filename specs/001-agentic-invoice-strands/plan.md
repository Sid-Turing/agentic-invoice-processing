# Implementation Plan: Agentic Invoice Processing (Strands)

**Branch**: `001-agentic-invoice-strands` | **Date**: 2026-07-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-agentic-invoice-strands/spec.md`

## Summary

Rebuild the multi-service invoice pipeline as a single **Strands** agent behind a
ChatGPT-style multimodal chat API. A user sends messages (free text and/or
uploaded invoice/PO files) across multi-turn conversations; an **Orchestrator
agent** (OpenAI model) drives the flow with five tools — vision extraction
(Gemini), PO lookup (DB read), PO upsert + decision persistence (DB write), and a
deterministic calculator — while performing validation and reconciliation by its
own reasoning. It resolves the PO from an uploaded document (extract → upsert) or
from the database by the invoice's PO number, reconciles invoice ↔ PO, persists
the result, and replies conversationally with a structured `Decision`. Storage is
SQLite via SQLAlchemy, seeded from the project CSVs. New standalone repo; no email
service, no frontend. See [research.md](./research.md) for the 10 design
decisions (R1 agent topology, R2 provider split, R3 image routing, R5 conversation
state are the cruxes).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: `strands-agents[openai,gemini]` (agent loop + `OpenAIModel`/`GeminiModel`), FastAPI + `uvicorn[standard]` + `python-multipart` (chat API/upload), SQLAlchemy 2.0 + `psycopg2-binary` + Alembic (persistence + migrations), `pdf2image` + Pillow (PDF→image), Pydantic v2 (schemas), `python-dotenv` (local config)
**Storage**: PostgreSQL via SQLAlchemy 2.0 (connection from `DATABASE_URL`, swappable); schema created from scratch by Alembic (`alembic upgrade head`); reference tables seeded from the three PO CSVs; dialect-portable ORM types so SQLite in-memory works for unit tests
**Testing**: `pytest` + `pytest-cov`; FastAPI `TestClient` (`httpx`) for integration; providers stubbed and a deterministic fake agent injected via an `AGENT_FACTORY` seam
**Target Platform**: Local single-user service (Linux/macOS), Python ASGI (uvicorn)
**Project Type**: Backend web service (agentic) — no frontend, no CLI
**Performance Goals**: A single-page, no-reconciliation turn returns in < 60 s (SC-007); interactive latency dominated by model round-trips
**Constraints**: External infra = a PostgreSQL instance (local Docker fine) + model APIs + poppler; raw upload bytes never persisted (SEC-003); DB writes confined to PO upsert + result persistence, no deletes (SEC-004); secrets + `DATABASE_URL` from env only
**Scale/Scope**: One invoice (+ optional PO) per turn; single user; alpha/demo scale. ~10–15 source modules; estimated < 2000 added lines.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

> This is a **new standalone repository**, not part of `humain-marketplace`. The
> Humain constitution's *principles* (persona value, TDD, secrets hygiene,
> reusable core, schema-first, minimal change) are applied as good practice; its
> *platform specifics* (React frontend, `develop`-targeted PRs, the Humain
> "platform secrets service", the `src/`/`backend/` layout) do not literally
> apply and are mapped to this repo's equivalents, noted per gate.

- **Persona-Scoped Product Value**: PASS. Single persona — an accounts-payable /
  finance operator. P1 (US1: process an invoice through chat) is independently
  demonstrable via `POST /chat`. Out-of-scope behavior is declared in the spec
  (no email, no UI, no PO management, no auth).
- **Branch/PR Discipline**: PASS (adapted). Work lands on a `feat/...` branch of
  the new repo, Conventional Commits, one logical change, estimated < 2000 lines
  (well under the 5000 gate). No `develop` in this repo — the base branch is `main`.
- **Security, Secrets, and Tenant Isolation**: PASS (adapted). No tenants/auth by
  design (SEC-001, explicit). Secrets — OpenAI/Gemini keys and `DATABASE_URL` —
  come from the environment / a gitignored `.env`; none committed (SEC-002). No
  Humain platform secrets service exists here; env is the runtime source and is
  the documented deviation. `.gitignore` already excludes `.env` and `*.db`.
- **Testable Increment Quality**: PASS. `tasks.md` will order tests before
  implementation for the core (schemas, repository, tools, decision assembly) and
  for both HTTP endpoints. Integration tests exercise `POST /chat` and `GET /health`
  with stubbed providers. Coverage: 80% target on `app/` core (services/db/tools),
  excluding the thin live-provider call sites (documented, covered via the fake-agent
  seam). Validation commands named below.
- **Minimal Maintainable Change**: PASS. Functional-first — tools, services, and
  repository functions are plain functions; the only classes are framework-mandated
  (Pydantic models, SQLAlchemy ORM models, the Strands `Agent`). New runtime deps
  are justified in research.md's license table; `psycopg2-binary` carries the
  LGPL-with-exception license (kept from the original; a strict LGPL gate would
  swap it for BSD `pg8000`). The design still *drops* deps vs. the original
  (`pandas`, `numpy`, `pytesseract`, `aiohttp`, `google-cloud-storage`).
- **Reusable-Core-First Architecture**: PASS. Business logic lives in
  `app/services/` (extraction, pdf, decision assembly), `app/db/` (repository), and
  `app/agent/tools/`; FastAPI handlers in `app/api/` are thin and delegate. Core
  modules are testable without the HTTP layer (repository against in-memory SQLite;
  tools with stubbed providers; decision logic pure).
- **HTTP API Schema Contracts**: PASS. `ChatResponse`, `Decision`, `Check`,
  `ReasonCode`, `HealthResponse`, `ExtractedInvoice`, `PurchaseOrder` are defined in
  [data-model.md](./data-model.md) and [contracts/](./contracts/) before
  implementation tasks. No breaking changes (greenfield).

**Result**: All gates PASS. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/001-agentic-invoice-strands/
├── plan.md              # This file
├── research.md          # Phase 0 — 10 design decisions
├── data-model.md        # Phase 1 — Pydantic + ORM schemas
├── quickstart.md        # Phase 1 — local run + smoke test
├── contracts/           # Phase 1 — chat-endpoint, health-endpoint, agent-tools
└── tasks.md             # Phase 2 — created by /speckit.tasks (NOT here)
```

### Source Code (repository root: `agentic-invoice-processing/`)

```text
app/
├── main.py                     # FastAPI app; startup seeding; router registration
├── config.py                   # Settings from env (keys, model ids, DB url, tolerances, currencies)
├── api/
│   ├── chat.py                 # POST /chat handler (thin: parse multipart -> agent turn -> ChatResponse)
│   └── health.py               # GET /health
├── schemas/
│   ├── chat.py                 # ChatResponse, HealthResponse
│   ├── decision.py             # Decision, Check, ReasonCode
│   ├── invoice.py              # ExtractedInvoice, InvoiceLineItem, VendorInfo, CustomerInfo
│   └── purchase_order.py       # PurchaseOrder, POLineItem
├── agent/
│   ├── orchestrator.py         # build_agent(): OpenAIModel + system prompt + tools + conversation mgr
│   ├── conversation.py         # per-conversation Agent registry + locks; request-scoped attachment contextvar
│   ├── prompts.py              # SINGLE prompt home: ORCHESTRATOR_SYSTEM_PROMPT + INVOICE_EXTRACTION_PROMPT + PO_EXTRACTION_PROMPT (named constants; imported by orchestrator + extraction_service)
│   └── tools/
│       ├── extraction.py       # extract_document  (Gemini structured output)
│       ├── po_lookup.py        # lookup_purchase_order  (DB read)
│       ├── persistence.py      # store_purchase_order, store_decision  (DB write)
│       └── math_tool.py        # calculate  (safe AST eval)
├── services/
│   ├── pdf_service.py          # pdf bytes -> [png bytes] (pdf2image, 300 dpi, Pillow downscale)
│   ├── extraction_service.py   # Gemini call -> ExtractedInvoice/PurchaseOrder (imports its prompt from agent/prompts.py; no inline prompt text)
│   └── decision_service.py     # (pure helpers) verdict-from-checks rule, tolerance comparisons
└── db/
    ├── database.py             # engine/session factory (from DATABASE_URL)
    ├── models.py               # ORM (portable types): PoVendor, PurchaseOrder, PoLineItem, ProcessedInvoice
    ├── repository.py           # get_po_by_number, upsert_purchase_order, persist_decision
    └── seed.py                 # seed_reference_data() from CSVs (skip-if-exists)

alembic/
├── env.py                      # reads DATABASE_URL + app models' metadata
└── versions/
    └── 0001_initial.py         # create the 4 tables from scratch
alembic.ini                     # (repo root) migration config

data/
├── purchase_orders_data.csv    # seed (copied from project root)
├── po_vendors_data.csv
└── purchase_order_line_items_data.csv

tests/
├── unit/                       # pdf, calculate, decision rule, repository (in-memory sqlite), tools (stubbed)
├── integration/                # POST /chat (all paths) + GET /health via TestClient + fake agent
├── fixtures/                   # sample invoice/PO documents + expected decisions
└── conftest.py                 # in-memory DB, AGENT_FACTORY override, provider stubs

pyproject.toml                  # deps + [dev] extra; pytest/coverage config
.env.example
README.md
```

**Structure Decision**: A single Python package `app/` for the backend service
(no `src/`/frontend split — there is no frontend). Layering follows
Reusable-Core-First: `db/` and `services/` hold pure logic, `agent/tools/` wrap
them as Strands tools, `agent/orchestrator.py` composes the agent, and `api/`
handlers are thin. **All prompt text lives in one place — `app/agent/prompts.py`**
as named constants (orchestrator system prompt + the invoice/PO extraction
prompts); `extraction_service.py` and `orchestrator.py` import from it and hold no
inline prompt strings. This is the concrete layout referenced by `/speckit.tasks`.

## Local Validation Commands

- **DB setup**: `alembic upgrade head` (creates the 4 tables in the `DATABASE_URL`
  Postgres), then reference-data seeding runs on startup (skip-if-exists).
- **Startup / import check (VAL-001)**: `python -c "import app.main"` and
  `uvicorn app.main:app --port 8000` → `GET /health` returns `status: "ok"`
  (with `database: true`).
- **Tests + coverage (VAL-003/004)**: `pytest --cov=app --cov-report=term-missing`
  (target ≥ 80% on core; live-provider call sites excluded and covered via the
  fake-agent seam).
- **Smoke (VAL-002)**: the three `curl` flows in [quickstart.md](./quickstart.md)
  (PO-on-file, uploaded-PO, multi-turn) captured as sample transcripts.

## Complexity Tracking

No constitution gate failed; no entries required.
