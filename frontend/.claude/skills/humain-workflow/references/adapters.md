# Persistence, validation, and publication adapters

Adapters translate package operations into consumer infrastructure. They receive immutable document snapshots plus an `operationId`, `idempotencyKey`, and `AbortSignal`.

## Persistence

`load` returns a document and opaque revision, `not_found`, or a structured failure. `save` receives `expectedRevision` when known and returns:

- `success` with a new durable revision
- `conflict` with the current server revision
- `failure` with `{ code, message, retryable }`
- `aborted`

```ts
import type { WorkflowPersistenceAdapter } from '@humain/workflow';

export const persistence: WorkflowPersistenceAdapter = {
  async load({ workflowId, signal }) {
    return workflowApi.load(workflowId, { signal });
  },
  async save({ document, expectedRevision, idempotencyKey, signal }) {
    return workflowApi.save(document.id, {
      document,
      expectedRevision,
      idempotencyKey,
      signal,
    });
  },
};
```

The server generates revisions. Never derive them from local timestamps. A conflict is not a generic retryable error: surface it and let product policy reload, merge, or fork.

## Product validation

Structural validation is package-owned. Supply a `WorkflowProductValidator` for business rules such as permissions, environment readiness, quotas, or publish policy. Return stable issue codes and paths suitable for UI display.

## Publication

Publication is a separate durable side effect. Pass the saved revision when the backend requires one, but enforce “must be clean and saved” in the consumer adapter or surrounding product policy; the package does not invent that policy.

Return `outcome_unknown` when a request may have committed but its response was lost. Do not classify it as ordinary failure and do not automatically retry. Query publication state using the idempotency key or another durable correlation identifier before the user retries.

Honor the signal at the HTTP, queue, or client boundary. A locally aborted request may still have committed remotely, so destructive or publication operations still need idempotency and reconciliation.
