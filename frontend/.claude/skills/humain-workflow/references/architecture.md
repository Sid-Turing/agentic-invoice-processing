# Architecture and ownership

`@humain/workflow` is a React editor runtime, not a workflow backend. Its deepest public boundary is the `WorkflowDocument`: a versioned, JSON-safe description of nodes, edges, positions, and viewport.

## Package-owned behavior

- Graph editing and projection
- Undo and redo history
- Structural validation against a node registry
- Selection, shortcuts, focus, and announcements
- Persistence, publication, validation, and execution controllers
- Operation cancellation, stale-result suppression, and safe state transitions

## Consumer-owned behavior

- Storage, APIs, queues, and authentication
- Tenant and authorization policy
- Product-specific configuration validation
- Revision generation and conflict resolution
- Publication semantics and deployed artifact lifecycle
- Workflow execution and observability infrastructure

The consumer supplies adapters. No HUMAIN backend client is embedded.

## Dependency boundary

Import runtime and type contracts from `@humain/workflow`. Compose custom renderer UI from `@humain/ui`. The graph library is a private implementation dependency: never import it, depend on its node or edge types, or persist its internal state.

Keep three layers separate:

1. Domain: documents, registry definitions, validation, migrations.
2. Application: adapters, permissions, API clients, revision and retry policy.
3. Presentation: `WorkflowEditor`, custom renderers, inspectors, and surrounding product UI.

This separation lets consumers replace their backend or rendering details without migrating stored workflow JSON.

## Controlled ownership

Use `document` plus `onDocumentChange` when an external store is authoritative. Apply each proposal to that store and pass the accepted document back. Use `defaultDocument` when the editor owns its session state. `workflowId` plus a persistence adapter may load a remote document into an uncontrolled session.

Do not pass both models opportunistically; decide authority before integration.
