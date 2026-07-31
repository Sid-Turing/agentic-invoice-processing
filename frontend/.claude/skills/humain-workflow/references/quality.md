# Quality and release checks

Test through the public package boundary, not through private graph-engine
implementation details. Cover ordered preset subsets, message/configure
precedence, explicit visual kinds, JSON-only documents, semantic data and tool
ports, controlled and uncontrolled ownership, all host adapters, keyboard
accessibility, cancellation, conflicts, stale results, and unknown publication
outcomes. Include controlled outline state, filtering above eight items,
source-order and keyboard behavior, simulation/live confirmation ownership,
fully configured outline/execution copy, and disabled-node candidate versus
stored-edge validation.

## Required repository order

Run these checks in order after changing the workflow public contract:

```bash
bun run typecheck:workflow
bun run build:workflow
bun run test:workflow -- packages/workflow/tests/public-api.test.ts packages/workflow/tests/public-types.test.ts packages/workflow/tests/public-bundle-exports.test.ts
bun run generate:workflow-skill
bun run check:workflow-skill
```

`typecheck:workflow` compiles the dedicated public consumer fixture in addition
to package source. Build before declaration and runtime-bundle boundary tests.
Generate the workflow skill archive only from its Markdown source; never edit
`humain-workflow.skill` by hand.

Then run the relevant focused unit, accessibility, visual, and integration
checks for the changed behavior. Before review, run Biome on changed
TypeScript/JSON files and `git diff --check`.

For skill source, archive, and installer changes, run these exact focused
checks as well:

```bash
bun test tooling/release/__tests__/workflow-skill-package.test.ts
bun test tooling/release/__tests__/workflow-skill-installer.test.ts
```

## Public-boundary review

Confirm all consumer imports use the public `@humain/workflow` root,
`@humain/workflow/domain`, `@humain/workflow/runtime`,
`@humain/workflow/editor`, `@humain/ui`, React, and the two public
stylesheets. Search consumer code, docs, and skills for package source paths,
`/internal/`, or `@xyflow/react`; none may cross the boundary. Keep package
exports limited to those documented entries and `./styles.css`.

Confirm built declarations and runtime exports include the preset factories and
defaults, editor-message factory and defaults, `WorkflowEditor` message prop,
and `visualKind` contract while exposing no XYFlow or React Flow symbols.

## Consumer verification

In a consuming application, run the equivalents of:

```bash
npx tsc --noEmit
npm test -- workflow
npm run build
```

Also confirm both public styles import once, documents remain JSON-safe,
credentials and services remain host-owned, and adapter/validator messages are
handled by the host. Do not treat Storybook appearance alone as evidence of a
release-safe integration.
