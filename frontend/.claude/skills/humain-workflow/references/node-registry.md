# Presets, registries, and renderers

Use `createWorkflowPresetDefinitions` for an official semantic catalog. Its
`include` array preserves consumer order, messages adjust preset copy, and
`configure` runs after messages with final authority over copy, ports, and
other definition fields.

```tsx
import {
  createWorkflowNodeRegistry,
  createWorkflowPresetDefinitions,
  type WorkflowNodeDefinition,
} from '@humain/workflow';

const presetDefinitions = createWorkflowPresetDefinitions({
  include: ['manual-trigger', 'ai-agent', 'http-request'],
  messages: {
    'manual-trigger': { displayName: 'Start support flow' },
    'ai-agent': {
      ports: {
        'tool-primary': { label: 'Approved tools', supportingText: 'Tools' },
      },
    },
  },
  configure: {
    'ai-agent': (definition) => ({
      ...definition,
      displayName: `${definition.displayName} (configured)`,
      ports: definition.ports.map((port) =>
        port.id === 'tool-primary' ? { ...port, maxConnections: 2 } : port,
      ),
    }),
  },
});

const productReview: WorkflowNodeDefinition = {
  typeId: 'product-review',
  displayName: 'Product review',
  category: 'Product',
  ports: [
    {
      id: 'input',
      label: 'Case input',
      direction: 'input',
      kind: 'data',
      placement: 'left',
      maxConnections: 1,
    },
    {
      id: 'output',
      label: 'Review output',
      direction: 'output',
      kind: 'data',
      placement: 'right',
    },
  ],
  defaultConfiguration: { queue: 'product-review' },
  renderer: {
    kind: 'builtin',
    id: 'tile',
    size: 'xl',
    visualKind: 'approval',
  },
};

const registry = createWorkflowNodeRegistry([
  ...presetDefinitions,
  productReview,
]);
```

The default AI Agent allows unlimited `tool-primary` connections; the example
sets a product-specific maximum of two. New built-in definitions must state a
renderer-family-valid `visualKind`: `card` and `tile` use a node visual kind,
while `circle` uses a circle visual kind and renders its label as text below the
icon. Omitted kinds are legacy compatibility only. Custom renderers remain
React-only and receive public node data, accessibility text, and editor
commands, never graph-engine values.

The default `http-request` is an AI tool with a `tool-input` control port. To
make it a linear data step, explicitly replace its ports after selecting it:

```tsx
const linearHttp = createWorkflowPresetDefinitions({
  include: ['http-request'],
  configure: {
    'http-request': (definition) => ({
      ...definition,
      ports: [
        {
          id: 'input',
          label: 'Request input',
          direction: 'input',
          kind: 'data',
          placement: 'left',
          maxConnections: 1,
        },
        {
          id: 'output',
          label: 'Request output',
          direction: 'output',
          kind: 'data',
          placement: 'right',
        },
      ],
    }),
  },
});
```

Keep type IDs and port IDs stable after publishing or migrate documents
explicitly. Persist only JSON-safe node configuration and document metadata;
keep functions, clients, credentials, and secrets outside stored documents.
