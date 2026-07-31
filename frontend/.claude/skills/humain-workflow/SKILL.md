---
name: humain-workflow
description: Use when building, integrating, extending, reviewing, or debugging React product workflow editors with @humain/workflow, including presets, documents, node registries, copy, adapters, accessibility, and release-safe verification.
---

# HUMAIN Workflow

Build React-only workflow editors with `@humain/workflow` and
`@humain/ui`. The package owns interaction, graph projection, structural
validation, history, copy, and operation controllers. The host owns storage,
product validation, side effects, authentication, credentials, backend clients,
and security.

Use only public `@humain/workflow`, `@humain/ui`, and stylesheet imports. Do
not import source paths, internals, or `@xyflow/react`; the graph engine is
private.

## Pre-flight

Before editing:

1. Confirm React 18 or 19 and install `@humain/ui`, `@humain/workflow`, and `lucide-react`.
2. Import `@humain/ui/styles.css` and `@humain/workflow/styles.css` once at the application entrypoint, then wrap the editor in `ThemeProvider`.
3. Start from an ordered `createWorkflowPresetDefinitions({ include })` subset; the supplied order is the product catalog order.
4. Choose controlled (`document` plus `onDocumentChange`) or uncontrolled (`defaultDocument`) ownership. Do not mix them.
5. Define server-authoritative revision, cancellation, idempotency, authentication, and outcome rules before implementing adapters.

Start with [quickstart.md](references/quickstart.md). Read
[architecture.md](references/architecture.md) for package boundaries.

## Route by task

| Task | Read |
|---|---|
| Integrate presets, documents, state ownership, or adapters | [quickstart.md](references/quickstart.md) |
| Add node types, ports, custom UI, or customize a preset | [node-registry.md](references/node-registry.md) |
| Load, save, validate, or publish | [adapters.md](references/adapters.md) |
| Stream runs, cancellation, or retries | [execution.md](references/execution.md) |
| Configure the outline, execution entry points, or disabled-node connections | [outline-and-interactions.md](references/outline-and-interactions.md) |
| Theme, copy, keyboard, focus, or announcements | [styling-and-accessibility.md](references/styling-and-accessibility.md) |
| Test, review, pack, or ship | [quality.md](references/quality.md) |

## Non-negotiable contracts

- Store only JSON-safe values in documents, including explicit source and target port IDs. Keep React elements, functions, clients, and secrets in the registry or host layer.
- Preserve semantic connections: ordinary flow uses `output` to `input`; the default AI tool relationship uses `tool-primary` to `tool-input`.
- Use preset messages for preset copy, then `configure` for final topology or copy. `configure` runs after messages.
- State `visualKind` on new built-in definitions. It must match the built-in renderer family; legacy omitted kinds only retain compatibility behavior.
- The default `http-request` preset is an AI tool. Replace its ports through an explicit `configure` callback only when the product needs a linear data step.
- Resolve package-owned copy with `createWorkflowEditorMessages`. Required accessible labels and formatter results cannot be empty; host adapter and validator messages remain unformatted host copy.
- Reject new and reconnected edges with disabled endpoints, but preserve an otherwise-valid stored edge when an existing node is disabled.
- Treat revisions as opaque server authority, `outcome_unknown` publication as indeterminate, and cancellation/idempotency context as mandatory adapter input.
- Validate parsed documents and registry compatibility before side effects.

## Implementation loop

Create the preset subset and registry first, add product definitions and host
adapters at the application boundary, then render `WorkflowEditor` inside
`ThemeProvider`. Exercise both ownership models, keyboard editing, accessible
names, conflicts, cancellation, stale runs, and unknown outcomes. End every
response with the focused tests, TypeScript check, and production build from
[quality.md](references/quality.md).
