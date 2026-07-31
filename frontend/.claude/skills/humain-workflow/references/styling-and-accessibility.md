# Styling, copy, and accessibility

Import `@humain/ui/styles.css` and `@humain/workflow/styles.css` once, and
wrap the editor in `ThemeProvider` from `@humain/ui`. Use public HUMAIN tokens
and surrounding layout; never copy package CSS, target private graph classes,
or import `@xyflow/react`.

## Package-owned message contract

Use `createWorkflowEditorMessages` for package-owned copy:

```tsx
import { createWorkflowEditorMessages } from '@humain/workflow';

const messages = createWorkflowEditorMessages({
  editor: {
    ariaLabel: ({ documentName }) => `${documentName} product workflow`,
  },
  header: { saveLabel: 'Save product workflow' },
  picker: { catalogSearchLabel: 'Search product nodes' },
  accessibility: {
    portLabel: ({ direction, portLabel }) => `${portLabel}, ${direction}`,
  },
});
```

A valid override leaf wins over the matching English default; missing siblings
fall back individually. For standalone public components, direct copy props win
over focused `messages`, which win over defaults. Inside `WorkflowEditor`, the
resolved editor tree is the one package-owned source of copy.

Required accessible labels and formatter results must be non-empty after
trimming. Development throws with the exact message path; production uses the
matching English fallback. This protects editor, picker, node, port, edge,
toolbar, dialog, and keyboard-action names. Empty visible-only copy remains
valid only where the message contract permits it.

Package validation formatters apply only to package-created issues. Consumer
validator and adapter messages remain host-owned and pass through unformatted;
localize them in the host service rather than by changing package formatters.

The `outline` and `execution` groups configure every package-owned workflow
steps label, count, filter, ordinal, current/status value, execution action,
and live-confirmation string. Pass the resolved full messages to
`WorkflowEditor`; pass `messages.outline` to a standalone
`WorkflowGraphOutline`. See
[outline-and-interactions.md](outline-and-interactions.md) for a complete
focused override and controlled example.

## Semantic and keyboard requirements

Give nodes meaningful `displayName` values and ports non-empty full `label`
values. `supportingText` is compact visible context, not a substitute for the
accessible port name. Store explicit JSON-safe edge port IDs so data flow is
`output` to `input` and the AI tool link is `tool-primary` to `tool-input`.

Test keyboard-only add/connect/select/duplicate/delete/undo/redo flows, focus
after pickers and inspectors close, visible focus in light and dark themes,
reduced motion, narrow layouts, 200% zoom, and supported forced-colors or
high-contrast modes. Preserve the editor shortcut and focus model instead of
adding document-level gestures around custom renderers.

Activated edges show a one-shot, path-bound execution tracer by default. The
tracer derives its core from the source port tone and its halo from the source
node tone, stops at the target, and is hidden under reduced motion. Set
`showExecutionFlowAnimation={false}` when a product needs execution colors
without spatial motion.

The editor remains React-only. Authentication, authorization, credentials,
secrets, backend services, and security policy stay host-owned.
