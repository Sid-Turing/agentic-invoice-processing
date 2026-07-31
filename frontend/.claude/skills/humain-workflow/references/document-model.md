# Document model

`WorkflowDocument` is the durable interchange format. It contains:

- `schemaVersion`, `id`, and `name`
- JSON-safe optional metadata
- nodes with stable IDs, registered type IDs, positions, and JSON object configuration
- edges that connect explicit source and target port IDs
- an optional viewport

Never persist registry definitions, renderer functions, React elements, API clients, class instances, `Date`, `Map`, or secrets in a document.

## Parse, migrate, validate

Treat loaded JSON as `unknown`:

```ts
import {
  migrateWorkflowDocument,
  validateWorkflowDocument,
} from '@humain/workflow';

const parsed = migrateWorkflowDocument(raw, migrations);
if (!parsed.ok) throw new Error(parsed.error.message);

const validation = validateWorkflowDocument(parsed.document, registry, {
  cyclePolicy: 'error',
});
if (!validation.valid) {
  throw new Error(validation.errors.map((issue) => issue.message).join('\n'));
}
```

Use the migration API only for explicit schema transitions. Keep migrations deterministic, side-effect free, and covered by fixtures from every supported source version.

Structural parsing answers “is this supported workflow JSON?” Registry validation answers “can this product interpret its node types and connections?” Product validation answers “is this workflow allowed or ready for this consumer?” Keep all three checks distinct.

## Disabled nodes and stored edges

Set `metadata.enabled` to `false` to disable a node while preserving its JSON
configuration and topology. Keep connection admission separate from document
validation:

- `validateWorkflowConnection` rejects a new or reconnected candidate when its
  source or target node is disabled.
- `validateWorkflowDocument` permits an otherwise-valid stored edge attached
  to a disabled node. Disabling a node therefore does not by itself block save,
  validated autosave, publication, or execution.

Stored edges still fail structural validation for missing nodes or ports, port
direction, kind compatibility, duplicates, capacity, and the configured cycle
policy. Do not delete durable edges merely to represent a temporarily disabled
node.

## Stable identity

Node and edge IDs are durable identity, not array indexes. Preserve them across edits and migrations. When duplicating or generating graph elements, create collision-resistant IDs in the consumer or through editor commands. Port IDs are part of each node type’s public contract; changing them requires a document migration.
