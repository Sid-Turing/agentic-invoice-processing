# Outline, interactions, and durable connections

Use the public `WorkflowGraphOutline` when a product needs workflow-step
navigation outside `WorkflowEditor`. The outline accepts consumer-created
items and run state; it does not read a document or execute a backend by
itself.

## Controlled standalone outline

Configure every outline and live-confirmation string through the same public
message factory used by the editor:

```tsx
import {
  createWorkflowEditorMessages,
  type WorkflowGraphOutlineItem,
  type WorkflowNodeExecutionStatus,
  type WorkflowRunStatus,
  WorkflowGraphOutline,
} from '@humain/workflow';
import { useState } from 'react';

const statusLabels: Record<WorkflowNodeExecutionStatus, string> = {
  failed: 'Needs attention',
  queued: 'Queued',
  running: 'Running',
  skipped: 'Skipped',
  succeeded: 'Completed',
  warned: 'Completed with warnings',
};

const messages = createWorkflowEditorMessages({
  outline: {
    openLabel: 'Open automation steps',
    closeLabel: 'Close automation steps',
    ariaLabel: 'Automation steps',
    heading: 'Automation steps',
    nodeCount: ({ count }) =>
      `${count} automation ${count === 1 ? 'step' : 'steps'}`,
    filterLabel: 'Find an automation step',
    filterPlaceholder: 'Search automation steps',
    filterNoResults: 'No automation steps match your search.',
    stepOrdinal: ({ position }) => `Step ${position}`,
    currentStepLabel: 'Current automation step',
    notStartedLabel: 'Waiting',
    statusLabel: ({ status }) => statusLabels[status],
    cancelRunLabel: 'Stop automation',
    retryRunLabel: 'Run automation again',
    testWorkflowLabel: 'Test automation in sandbox',
    testWorkflowText: 'Test in sandbox',
    runWorkflowLabel: 'Run automation',
  },
  execution: {
    liveConfirmationTitle: 'Run automation?',
    liveConfirmationEffectsDescription:
      'This may update connected systems and notify users.',
    cancelLabel: 'Keep editing',
    confirmLabel: 'Run automation',
  },
});

interface ProductOutlineProps {
  items: readonly WorkflowGraphOutlineItem[];
  runStatus: WorkflowRunStatus;
  confirmLiveRun(): Promise<boolean>;
  execute(): void;
}

export function ProductOutline({
  items,
  runStatus,
  confirmLiveRun,
  execute,
}: ProductOutlineProps) {
  const [open, setOpen] = useState(false);
  const [selectedNodeId, setSelectedNodeId] = useState<string>();

  return (
    <WorkflowGraphOutline
      executionMode="live"
      items={items}
      messages={messages.outline}
      onExecute={() => {
        void confirmLiveRun().then((confirmed) => {
          if (confirmed) execute();
        });
      }}
      onOpenChange={setOpen}
      onSelectNode={setSelectedNodeId}
      open={open}
      runStatus={runStatus}
      selectedNodeIds={selectedNodeId ? [selectedNodeId] : []}
      showExecutionControl
    />
  );
}
```

The standalone `onExecute`, `onRetry`, and `onCancel` callbacks are consumer
policy. In live mode, wrap `onExecute` and `onRetry` in consumer confirmation;
the outline supplies mode-aware warning copy but does not open the editor's
dialog. Set `showExecutionControl={false}` when the host renders actions
elsewhere. Set `disabled` when execution is unavailable.

Inside `WorkflowEditor`, pass the full `messages` object and set
`executionMode="live"` when the active adapter can cause side effects. The
editor then owns the centralized confirmation boundary for all editor
execution entry points, including retry. Simulation is the default and starts
immediately. Keep `executionMode` and the execution adapter under the same
React-owned configuration.

## Navigation behavior

- `open` plus `onOpenChange` is controlled disclosure state;
  `defaultOpen` is the uncontrolled alternative. Do not combine both models.
- `items` remain in consumer-supplied source order. `selectedNodeIds` marks the
  first matching item current with `aria-current="step"`; use `onSelectNode` to
  synchronize product selection.
- A search filter appears automatically with more than eight items. Filtering
  preserves source order and original ordinals. No matches retain the search
  field and show configured empty-result copy.
- Arrow Up and Arrow Down wrap through currently filtered items. Home and End
  move to the first and last visible items.
- `runStatus` selects execute, cancel, or retry presentation. Supply the
  matching callback; missing callbacks and `disabled` keep actions unavailable.

## Semantic and disabled-node connections

Persist explicit semantic port IDs. Ordinary data flow connects `output` to
`input`. The default AI Agent tool relationship connects `tool-primary` to a
tool's `tool-input`; do not replace either with graph-engine handles.

A disabled node remains part of the document:

```ts
const nextDocument = {
  ...document,
  nodes: document.nodes.map((node) =>
    node.id === 'http'
      ? { ...node, metadata: { ...node.metadata, enabled: false } }
      : node,
  ),
};
```

`validateWorkflowConnection` rejects a new or reconnected candidate when the
source or target is disabled. `validateWorkflowDocument` permits an
otherwise-valid stored edge attached to a disabled node. This distinction
preserves durable topology through save, validated autosave, publication, and
execution; disabling a node is not a request to delete its edges.

Stored edges still enforce missing-node and missing-port checks, direction and
kind compatibility, duplicate connections, port capacity, and the configured
cycle policy. Keep these structural checks package-owned. Any stricter product
rule belongs in the consumer validator.
