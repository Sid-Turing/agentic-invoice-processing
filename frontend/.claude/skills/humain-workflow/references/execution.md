# Execution streams

`WorkflowExecutionAdapter.execute` returns an `AsyncIterable<WorkflowExecutionEvent>`. The application decides how a workflow runs; the package reduces its event stream into stable editor state.

## Classify execution in React

`WorkflowEditor` defaults `executionMode` to `"simulation"`. Treat that mode as
host configuration, not something `@humain/workflow` can infer from the adapter
or document. If an execution adapter can cause side effects, explicitly render
`executionMode="live"` and update it whenever execution configuration changes.
Keep the mode and `adapters.execution` together in React state or props.

In live mode, `WorkflowEditor` confirms every editor entry point before it calls
the adapter. Changing the mode or replacing the execution adapter dismisses an
open confirmation; the user must make a fresh request. Without an execution
adapter, execution controls stay unavailable or disabled. A standalone
`WorkflowGraphOutline` only provides mode-aware labels—its callbacks retain
consumer-owned confirmation policy. See
[outline-and-interactions.md](outline-and-interactions.md) for the controlled
standalone pattern and outline behavior.

```ts
import type { WorkflowExecutionAdapter } from '@humain/workflow';

export const execution: WorkflowExecutionAdapter = {
  async *execute({ document, revision, idempotencyKey, signal }) {
    const stream = workflowApi.execute({
      document,
      revision,
      idempotencyKey,
      signal,
    });
    for await (const event of stream) {
      if (signal.aborted) return;
      yield event;
    }
  },
};
```

## Event contract

- Use one durable `runId` for the complete run.
- Start `sequence` at a documented value and increase it strictly for every event.
- Emit `run.queued` and `run.started` before node activity when applicable.
- Finish with exactly one terminal run event: `run.completed`, `run.failed`, or `run.cancelled`.
- Use node, edge, log, progress, and output events only for their documented payloads.

The controller distinguishes:

- `cancelled`: the current operation was deliberately aborted.
- `stale`: a newer execution superseded the current one; ignore its late result.
- `failed`: execution or stream processing failed.
- `completed`: a terminal completion event was reduced.

Do not collapse these states into a boolean. A stream ending without a terminal run result is a failure.

## Retry and idempotency

Each new execute call receives a new idempotency key. Forward it to the backend so reconnects and uncertain transport outcomes can be correlated. Never invent automatic execution retries unless the product has defined whether execution is repeatable. If a run may already exist, reconcile by idempotency key or run ID first.

A retry is a new request, not a continuation of the prior run. A live retry
opens editor confirmation again; simulation starts immediately. Custom
renderers should call `commands.execute` only when it is available and use
`commands.executeLabel` for its mode-aware action copy rather than calling a
host service directly.

Test late events after cancellation and supersession. They must not overwrite the active run’s state.

## Editing policies

`WorkflowEditor` locks structural edits while a run is queued or running by default. Selection and viewport changes remain available. Choose `executionEditingPolicy="warning-only"` only when the product explicitly permits the draft to diverge from the executing snapshot.

For `fork-on-edit`, supply `createFork`. It must return a valid workflow document with a new ID; the editor applies the requested structural command to that fork. Workflow identity, permissions, and persistence for the fork remain consumer-owned. Undo and redo stay blocked until the consumer is working on the fork.
