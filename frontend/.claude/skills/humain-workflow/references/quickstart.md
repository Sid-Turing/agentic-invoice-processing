# Preset-first quick start

Install the public runtime peers, then import the two public stylesheets once:

```bash
npm install @humain/ui @humain/workflow lucide-react
```

```tsx
import { ThemeProvider } from '@humain/ui';
import {
  createWorkflowEditorMessages,
  createWorkflowNodeRegistry,
  createWorkflowPresetDefinitions,
  type WorkflowDocument,
  type WorkflowEditorAdapters,
  type WorkflowExecutionMode,
  WorkflowEditor,
} from '@humain/workflow';
import { useState } from 'react';
import '@humain/ui/styles.css';
import '@humain/workflow/styles.css';

const definitions = createWorkflowPresetDefinitions({
  include: ['manual-trigger', 'ai-agent', 'http-request', 'workflow-end'],
});
const registry = createWorkflowNodeRegistry(definitions);

const initialDocument: WorkflowDocument = {
  schemaVersion: 1,
  id: 'welcome',
  name: 'Welcome workflow',
  nodes: [
    {
      id: 'start',
      type: 'manual-trigger',
      position: { x: 80, y: 220 },
      configuration: {},
    },
    {
      id: 'agent',
      type: 'ai-agent',
      position: { x: 360, y: 220 },
      configuration: {},
    },
    {
      id: 'http',
      type: 'http-request',
      position: { x: 360, y: 460 },
      configuration: {},
    },
    {
      id: 'end',
      type: 'workflow-end',
      position: { x: 660, y: 220 },
      configuration: {},
    },
  ],
  edges: [
    {
      id: 'start-to-agent',
      sourceNodeId: 'start',
      sourcePortId: 'output',
      targetNodeId: 'agent',
      targetPortId: 'input',
    },
    {
      id: 'agent-tool-to-http',
      sourceNodeId: 'agent',
      sourcePortId: 'tool-primary',
      targetNodeId: 'http',
      targetPortId: 'tool-input',
    },
    {
      id: 'agent-to-end',
      sourceNodeId: 'agent',
      sourcePortId: 'output',
      targetNodeId: 'end',
      targetPortId: 'input',
    },
  ],
};

const messages = createWorkflowEditorMessages({
  header: { saveLabel: 'Save workflow' },
  editor: { ariaLabel: ({ documentName }) => `${documentName} editor` },
  execution: {
    liveConfirmationTitle: 'Run workflow?',
    liveConfirmationEffectsDescription:
      'This may affect connected systems, send notifications, and require approvals.',
    cancelLabel: 'Cancel',
    confirmLabel: 'Run workflow',
  },
});

const executionMode: WorkflowExecutionMode = 'simulation';

const adapters: WorkflowEditorAdapters = {
  persistence: {
    async load() {
      return { status: 'not_found' };
    },
    async save() {
      return { status: 'success', revision: 'v1' };
    },
  },
  publication: {
    async publish() {
      return { status: 'success', publicationId: 'welcome', revision: 'v1' };
    },
  },
  execution: {
    async *execute() {
      yield { type: 'run.queued', runId: 'welcome-run', sequence: 1 };
      yield { type: 'run.completed', runId: 'welcome-run', sequence: 2 };
    },
  },
  validation: ({ structuralResult }) => structuralResult,
};

export function WorkflowScreen() {
  const [document, setDocument] = useState(initialDocument);

  return (
    <ThemeProvider>
      <WorkflowEditor
        adapters={adapters}
        document={document}
        executionMode={executionMode}
        messages={messages}
        nodeCatalogDefinitions={definitions}
        onDocumentChange={({ document: nextDocument }) =>
          setDocument(nextDocument)
        }
        registry={registry}
      />
    </ThemeProvider>
  );
}
```

`include` keeps the stated order. The document is JSON-only and preserves the
semantic data edges (`output` to `input`) plus the AI tool edge
(`tool-primary` to `tool-input`). Use `defaultDocument={initialDocument}`
instead of the controlled `document` state loop when the editor should own its
local session; do not combine both ownership models.

All adapters are host-owned: persistence, publication, execution, validation,
credentials, backend clients, authentication, authorization, secrets, and
security policy live outside the package. Adapter errors and consumer validator
messages are shown as supplied rather than reformatted by package copy.

`executionMode` defaults to `"simulation"`. If the active execution adapter can
cause side effects, pass `executionMode="live"` and update the prop whenever
the host execution configuration changes. The package does not infer adapter
safety or policy. In live mode, `WorkflowEditor` confirms every editor entry
point, including retry; a retry is a new request. Mode or adapter changes
dismiss a pending confirmation, unavailable adapters keep controls disabled,
and standalone `WorkflowGraphOutline` callbacks keep consumer-owned
confirmation policy. Custom renderer actions use optional
`commands.executeLabel` with optional `commands.execute` so their copy and
behavior enter the same editor boundary.

For a controlled standalone outline, complete outline and execution copy, and
the disabled-node connection rules, read
[outline-and-interactions.md](outline-and-interactions.md).

The root `@humain/workflow` entry remains supported. Prefer the narrowest
layered public entry when an application does not need the entire editor stack:

```ts
import {
  createWorkflowPresetRegistry,
  validateWorkflowDocument,
} from '@humain/workflow/domain';
import { createWorkflowExecutionController } from '@humain/workflow/runtime';
import { WorkflowEditor } from '@humain/workflow/editor';
```

Use `domain` for JSON-safe contracts and pure behavior, `runtime` for non-React
controllers and adapter state, and `editor` for React hooks, messages, and
components. Never import emitted internal paths or `@xyflow/react`.
