# Golden Paths Recipe

Use these three paths as the default starting point for production workflows. Keep implementations close to the library wrappers before adding custom composition.

This packaged recipe is the canonical consumer workflow reference.

## AI Chat

**Use:** AIContainer, AIMessage, AIInput
**Optional:** AIEmptyState, AIPromptSuggestion, AIFeedbackBar, Avatar, Button, Badge

- Build the shell with `AIContainer` compound components.
- Store messages in app state as `ChatMessage[]`.
- Pass `autoScrollKey` from the latest message id or streaming revision when rendering custom message children.
- Use `AIEmptyState` and `AIPromptSuggestion` for first-run prompts.
- Use `AIContainer.Input` for text, files, paste-as-file, drag/drop, disabled, and submit behavior.
- Keep retry, copy, feedback, and attachment actions keyboard reachable.

**Cover states:** empty, draft, sending, streaming/loading, success, error with retry, selected/uploading/failed attachments, long markdown/code/table content.

**Check:** mobile composer reachability, independent message scrolling, focus after submit/retry/remove, live announcement for new responses, no hidden latest message behind fixed UI.

**Avoid:** custom chat bubbles, generic cards for messages, toast-only failures, auto-submitting prompt suggestions, unbounded composer growth.

## Operational Dashboard

**Use:** AppShell or page layout, MetricCard, DataTable, BarChart, LineChart, DonutChart
**Optional:** Tabs, Select, Button, Badge, Tooltip, Pagination, Skeleton, Alert

- Lead with `MetricCard` for headline health.
- Use charts only when trend, comparison, or distribution helps users decide.
- Use `DataTable` for operational queues and row-level work.
- Keep time range, filters, freshness, and table controls visible.
- Prefer semantic tokens and components for status and sentiment.

**Cover states:** loading, empty, no matching filters, partial data, error with retry, stale data, default/applied/cleared filters, sorting, pagination, row selection, long labels, sparse/zero/missing chart values.

**Check:** keyboard table controls, chart information available as text, color not the only status signal, mobile stacking, table horizontal scroll, 200% zoom wrapping.

**Avoid:** custom KPI cards, decorative charts, raw status colors, hidden mobile controls, mixed time ranges without labels.

## Forms/Auth

**Use:** Form, Input, Select, Checkbox, Button
**Optional:** Textarea, Switch, RadioGroup, CheckboxGroup, NumberInput, FileInput, Alert, Dialog, Sonner

- Use field-aware controls directly with `label`, `description`, `error`, and `required`.
- Wrap flows in a real `<form>` and handle submit.
- Use browser `autoComplete` for auth fields.
- Keep values after validation or auth errors.
- Use `Button` loading state for submit work.

**Cover states:** initial, dirty/touched, validation error, submitting, auth error, success, disabled/read-only, forgot password, reset sent, expired link, MFA, locked account.

**Check:** visible labels, Enter submits, errors are associated and announced, focus moves on failed submit, touch targets are at least 44px, password managers and autofill work, mobile and 200% zoom hold.

**Avoid:** placeholder-only labels, hand-rolled field wrappers, clearing values on errors, silent disabled states, account-enumerating auth messages, div/button pseudo-forms.

## Verification

Run the consuming application's lint, typecheck, tests, and production build.
