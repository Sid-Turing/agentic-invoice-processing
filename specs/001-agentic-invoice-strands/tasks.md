# Tasks: Agentic Invoice Processing (Strands)

**Input**: Design documents from `specs/001-agentic-invoice-strands/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: REQUIRED (TDD). Test tasks precede their implementation tasks for all
schemas, DB/repository, services, tools, and both HTTP endpoints. Model-provider
calls are exercised via stubs / a deterministic fake agent injected through the
`AGENT_FACTORY` seam — no live provider calls in CI.

**Organization**: By user story. US1 (P1) is a complete, independently testable MVP.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable (different files, no dependency on an incomplete task)
- **[Story]**: US1 / US2 / US3 for user-story phases only
- All paths are relative to repo root `agentic-invoice-processing/`

## Path Conventions

Single Python package `app/` (backend service; no frontend/CLI). Tests under
`tests/unit/` and `tests/integration/`, fixtures under `tests/fixtures/`, seed
CSVs under `data/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project skeleton, dependencies, config, seed data.

- [ ] T001 Create package structure per plan.md: `app/`, `app/api/`, `app/schemas/`, `app/agent/tools/`, `app/services/`, `app/db/`, `data/`, `tests/unit/`, `tests/integration/`, `tests/fixtures/`, with `__init__.py` files
- [ ] T002 Author `pyproject.toml`: runtime deps `strands-agents[openai,gemini]`, `fastapi`, `uvicorn[standard]`, `python-multipart`, `sqlalchemy>=2.0`, `pdf2image`, `pillow`, `pydantic>=2`, `python-dotenv`; `[dev]` extra `pytest`, `pytest-cov`, `httpx`
- [ ] T003 [P] Add `.env.example` (OPENAI_API_KEY, GEMINI_API_KEY, OPENAI_MODEL_ID, GEMINI_MODEL_ID, DATABASE_URL, TAX_RATE, SUPPORTED_CURRENCIES, MAX_UPLOAD_MB) and extend `.gitignore` with `*.db` and `.env`
- [ ] T004 [P] Copy `purchase_orders_data.csv`, `po_vendors_data.csv`, `purchase_order_line_items_data.csv` from the original project root into `data/`
- [ ] T005 [P] Configure pytest + coverage in `pyproject.toml` (`--cov=app`) and create empty `tests/conftest.py`
- [ ] T006 Implement `app/config.py`: a settings object reading env (keys, model ids, `DATABASE_URL` default `sqlite:///./invoices.db`, `TAX_RATE=0.09125`, tolerances line/total 0.02, PO qty 0.10 / unit 0.05 / total 0.05, vendor-match 0.70, tax-discrepancy 0.25, `SUPPORTED_CURRENCIES=["USD"]`, `MAX_UPLOAD_MB=10`)

**Checkpoint**: `python -c "import app.config"` succeeds; deps install.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared schemas, persistence, services, tools, and the agent/app
scaffold that every user story depends on.

**⚠️ CRITICAL**: No user-story phase can begin until this phase is complete.

### Schemas (contracts-first)

- [ ] T007 [P] Write schema tests in `tests/unit/test_schemas.py` (numeric fields default null; `Decision.verdict==APPROVED` iff no `fail` check; `Check.status` enum; `Check.id`/`ReasonCode.code` taxonomy)
- [ ] T008 [P] Implement `app/schemas/invoice.py` (`VendorInfo`, `CustomerInfo`, `InvoiceLineItem`, `ExtractedInvoice`) per data-model.md
- [ ] T009 [P] Implement `app/schemas/purchase_order.py` (`POLineItem`, `PurchaseOrder` with `source` literal)
- [ ] T010 [P] Implement `app/schemas/decision.py` (`Check`, `ReasonCode`, `Decision`)
- [ ] T011 [P] Implement `app/schemas/chat.py` (`ChatResponse`, `HealthResponse`)

### Persistence

- [ ] T012 Write repository tests in `tests/unit/test_repository.py` against in-memory SQLite: `get_purchase_order_by_number` (found/not found), `upsert_purchase_order` (create + update-by-number + line-item replace), `persist_decision` (returns record_id), and the no-delete / upsert-only invariant
- [ ] T013 Implement `app/db/database.py` (SQLAlchemy 2.0 engine + session factory from `DATABASE_URL`; `get_session` dependency)
- [ ] T014 Implement `app/db/models.py` ORM: `PoVendor`, `PurchaseOrder` (unique `po_number`), `PoLineItem`, `ProcessedInvoice` (JSON columns) per data-model.md
- [ ] T015 Implement `app/db/repository.py`: `get_purchase_order_by_number`, `upsert_purchase_order`, `persist_decision` (pure data-access; make tests T012 pass)
- [ ] T016 [P] Write seed test in `tests/unit/test_seed.py` (loads 2 vendors / 2 POs / 15 line items; second call is a no-op — skip-if-exists)
- [ ] T017 Implement `app/db/seed.py` `seed_reference_data(session, data_dir)` using stdlib `csv`, skip-if-rows-exist

### Services (pure/core)

- [ ] T018 [P] Write `tests/unit/test_pdf_service.py` (multi-page PDF → N png byte blobs; oversized page downscaled ≤1600px)
- [ ] T019 [P] Implement `app/services/pdf_service.py` (`pdf2image` 300 dpi + Pillow downscale → `list[bytes]`)
- [ ] T020 [P] Write `tests/unit/test_decision_service.py` (verdict-from-checks rule; tolerance comparisons for line math, financial totals, PO qty/price; flat-rate tax expectation)
- [ ] T021 [P] Implement `app/services/decision_service.py` (pure helpers: `verdict_from_checks`, tolerance comparators, tax expectation — no I/O)
- [ ] T022 Write `tests/unit/test_extraction_service.py` with a stubbed Gemini client (returns a canned `ExtractedInvoice`/`PurchaseOrder`)
- [ ] T023 Implement `app/services/extraction_service.py` (`GeminiModel` structured-output call + carried-over extraction prompt; image content blocks; merge multi-page results)

### Tools (Strands `@tool` wrappers)

- [ ] T024 Write `tests/unit/test_tools.py` (calculate safe-eval incl. rejecting names/calls; `lookup_purchase_order` found/not-found; `store_purchase_order` upsert; `store_decision` returns record_id + stashes to contextvar; `extract_document` reads attachment contextvar, routes to extraction_service, returns error dict on unreadable)
- [ ] T025 [P] Implement `app/agent/tools/math_tool.py` `calculate(expression)` (AST-based safe evaluator)
- [ ] T026 [P] Implement `app/agent/tools/po_lookup.py` `lookup_purchase_order(po_number)` (opens session, calls repository)
- [ ] T027 [P] Implement `app/agent/tools/persistence.py` `store_purchase_order(purchase_order)` and `store_decision(decision)` (validate → repository → contextvar stash for the handler)
- [ ] T028 Implement `app/agent/tools/extraction.py` `extract_document(attachment_id, document_type)` (read bytes from attachment contextvar → `pdf_service` → `extraction_service`; return dict or `{"error","kind"}`)

### Agent + app scaffold

- [ ] T029 Implement `app/agent/conversation.py` (per-`conversation_id` registry `{id: (Agent, Lock)}` with `get_or_create`; request-scoped attachment `contextvar` set/reset helpers)
- [ ] T030 Implement `app/agent/prompts.py` (base system prompt: role, tool inventory, reason-code taxonomy, tolerances, "call `store_decision` once per processing turn")
- [ ] T031 Implement `app/agent/orchestrator.py` `build_agent(conversation_id)` (`OpenAIModel` + tools + `SlidingWindowConversationManager` + `callback_handler=None`) and an `AGENT_FACTORY` indirection seam for tests
- [ ] T032 Implement `app/main.py` (FastAPI app; on-startup `seed_reference_data`; router registration placeholder)
- [ ] T033 Write `tests/integration/test_health.py` (TestClient: `GET /health` → 200, providers/database flags, `status` ok/degraded)
- [ ] T034 Implement `app/api/health.py` `GET /health` → `HealthResponse` (key-configured checks + `SELECT 1`)
- [ ] T035 Build `tests/conftest.py`: in-memory SQLite fixture + `get_session` override, provider stubs, deterministic **fake agent** wired via `AGENT_FACTORY` (drives real tools in a fixed order), and a `tests/fixtures/` loader

**Checkpoint**: foundational tests (T007, T012, T016, T018, T020, T022, T024, T033) pass; `GET /health` returns `ok`. User-story work can begin.

---

## Phase 3: User Story 1 — Process an invoice through chat (Priority: P1) 🎯 MVP

**Goal**: A single chat turn with an uploaded invoice (and optionally a PO, or a PO
on file) yields a persisted `APPROVED`/`NEEDS_REVIEW` decision plus a natural-language reply.

**Independent test**: `POST /chat` with (a) an invoice referencing seeded `PO-54872`
→ `APPROVED`, `matched_po.source=="database"`; (b) an invoice + PO document →
`matched_po.source=="uploaded"` and the PO is now persisted; (c) a tampered total →
`NEEDS_REVIEW` with the right reason code.

- [ ] T036 [P] [US1] Write `tests/integration/test_chat_po_on_file.py` (invoice with a seeded PO number → APPROVED; tampered financial total → NEEDS_REVIEW `financial_totals`; divergent line item → `po_line_items_match`)
- [ ] T037 [P] [US1] Write `tests/integration/test_chat_uploaded_po.py` (invoice + PO parts → agent extracts + `store_purchase_order`, `matched_po.source=="uploaded"`; PO retrievable by number afterward)
- [ ] T038 [P] [US1] Add fixtures in `tests/fixtures/`: invoice referencing PO-54872, a tampered variant, and a matching invoice+PO pair (plus their expected decisions)
- [ ] T039 [US1] Implement `app/api/chat.py`: parse multipart (`message`, `conversation_id`, `invoice`, `po`), validate size/type (→413/415), assign `attachment_id`s, set the attachment contextvar, compose the user message (text + Attachments list), run one agent turn under the conversation lock via `await agent.invoke_async(...)`, read the stashed `Decision`, return `ChatResponse`
- [ ] T040 [US1] Extend `app/agent/prompts.py` with the single-turn workflow: extract invoice → resolve PO (uploaded → `extract_document`+`store_purchase_order`; else `lookup_purchase_order` by PO number; else skip w/ reason) → run all invoice-internal checks (using `calculate`) → reconcile vendor + line items within tolerances when a PO is resolved → assemble `Decision` → `store_decision` once
- [ ] T041 [US1] Register the chat router in `app/main.py` and map transient provider/DB failures to `503` (distinct from NEEDS_REVIEW=200)

**Checkpoint**: US1 tests pass; the MVP is demonstrable end-to-end via quickstart flow 1 & 2.

---

## Phase 4: User Story 2 — Converse and refine across turns (Priority: P2)

**Goal**: Multi-turn context — supply a PO (file or number) in a later turn to
update the earlier invoice's decision without re-upload; answer follow-ups from context.

**Independent test**: Turn 1 invoice-only (reconciliation skipped); turn 2 uploads
the matching PO under the same `conversation_id` → updated decision reconciled
against the turn-1 invoice; turn 3 plain-text "why?" → explanation, `decision==null`.

- [ ] T042 [P] [US2] Write `tests/integration/test_chat_multiturn.py` (PO-arrives-later reconciles the retained invoice; PO-number-in-text triggers lookup + reconcile)
- [ ] T043 [P] [US2] Write `tests/integration/test_chat_followup.py` (plain-text "why?" returns an explanation consistent with the prior decision and `decision==null`; same `conversation_id` continuity)
- [ ] T044 [US2] Verify/adjust `app/agent/conversation.py` so an existing `conversation_id` reuses its Agent (retained `messages`); confirm `SlidingWindowConversationManager` window retains the prior extracted-invoice turn
- [ ] T045 [US2] Extend `app/agent/prompts.py` with refinement obligations: use retained conversation context, re-reconcile & re-`store_decision` when a PO/number arrives later, and answer follow-up questions without re-invoking extraction

**Checkpoint**: US1 + US2 tests pass; quickstart flow 3 works.

---

## Phase 5: User Story 3 — Graceful, explainable conversation (Priority: P3)

**Goal**: Handle plain-text/ambiguous/incomplete input gracefully; expose a complete
check-by-check trace and the resolved PO source.

**Independent test**: A greeting yields a reply with no tool calls; an ambiguous
attachment yields a clarifying question (no fabricated decision); a processing turn's
`checks[]` lists every check with outcome, compared values, confidence/rationale, and PO source.

- [ ] T046 [P] [US3] Write `tests/integration/test_chat_conversational.py` (greeting → reply, no `store_decision`; ambiguous/unrelated attachment → clarifying question, `decision==null`)
- [ ] T047 [P] [US3] Write `tests/integration/test_decision_trace.py` (every check present with pass/fail/skipped + `compared`; semantic checks carry `confidence`+`rationale`; skipped reconciliation carries the distinguishing reason; `matched_po.source` set)
- [ ] T048 [US3] Extend `app/agent/prompts.py` with graceful-handling obligations: ask a clarifying question on ambiguity, never fabricate a decision, don't call tools on non-processing turns, and record skipped-check reasons (`no PO number` vs `PO not found`)
- [ ] T049 [US3] Ensure `app/services/decision_service.py` / trace assembly emits the full `Check` list (including `skipped` entries with reasons) so US3 trace assertions hold regardless of model phrasing

**Checkpoint**: all three stories pass independently and together.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T050 [P] Streaming variant (SHOULD, FR-024): add an SSE path to `app/api/chat.py` via `agent.stream_async` (`text/event-stream`, terminal `decision` event) + a streaming test in `tests/integration/test_chat_stream.py`
- [ ] T051 [P] Write `README.md` (setup incl. `poppler`, run, the three smoke flows) mirroring quickstart.md
- [ ] T052 [P] Error-handling & logging pass across `app/api/` and tools; confirm no secrets / `*.db` / raw upload bytes are persisted or committed
- [ ] T053 Coverage validation: `pytest --cov=app --cov-report=term-missing` ≥ 80% on core (`app/db`, `app/services`, `app/agent/tools`, `app/schemas`); document any excluded live-call lines
- [ ] T054 Final validation (quickstart): `python -c "import app.main"`, `uvicorn app.main:app` + `GET /health` = ok, and the three `curl` flows produce the expected decisions

---

## Dependencies & Execution Order

- **Setup (P1)** → **Foundational (P2)** → **US1 (P3)** → **US2 (P4)** → **US3 (P5)** → **Polish (P6)**.
- Foundational blocks all stories. Within Foundational: schemas (T007–T011) and pure services (T018–T021) are independent; DB (T012–T017) precedes tools that touch it (T026–T028); tools precede the orchestrator (T031); the app scaffold (T032–T035) precedes any integration test.
- **US1** depends only on Foundational and is the MVP. **US2** and **US3** depend on US1's chat handler + prompt (T039/T040) but are independent of each other — they extend the prompt and add tests, touching `app/agent/prompts.py` sequentially (not in parallel with each other).
- TDD: each test task precedes its implementation task and must fail first.

## Parallel Execution Examples

- **Setup**: T003, T004, T005 in parallel after T001/T002.
- **Foundational schemas**: T008, T009, T010, T011 in parallel (after T007).
- **Foundational services**: T018/T019, T020/T021 pairs in parallel with the schema group.
- **Foundational tools**: T025, T026, T027 in parallel (after DB + T024); T028 after T019/T023.
- **US1 tests**: T036, T037, T038 in parallel before implementing T039–T041.
- **Polish**: T050, T051, T052 in parallel.

## Implementation Strategy

- **MVP = Phase 1 + Phase 2 + Phase 3 (US1)** — a working chat endpoint that
  extracts, resolves a PO (uploaded or on file), validates, reconciles, persists,
  and replies with a structured decision. Ship/demo here.
- Add **US2** (multi-turn refinement) and **US3** (graceful/explainable) as
  incremental, independently testable slices.
- **Polish** (streaming, README, coverage, final validation) last.
- Total: **54 tasks** — Setup 6, Foundational 29, US1 6, US2 4, US3 4, Polish 5.
