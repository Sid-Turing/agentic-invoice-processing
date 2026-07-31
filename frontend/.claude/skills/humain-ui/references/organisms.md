# Organisms

Complex, self-contained sections.

## AI

### AIAsciiDiagram
Renders ASCII art diagrams

### AIChart
AI response chart block for bar, line, area, and pie visualizations

### AIClarificationCard
Schema-driven interactive AI response renderer for questions, choices, progress, and confirmations

### AICodeBlock
Code block with copy button, collapsible

Props: code, language, fileName, showHeader, showCopyButton, showLineNumbers, size (sm|md|lg)

```tsx
<AICodeBlock code="const x = 1" language="typescript" showCopyButton />
```

### AIComponent
Deprecated compatibility alias for the AIClarificationCard interactive AI response renderer

### AIContainer
Chat container with message list, input, auto-scroll, minimize

Props: messages, autoScrollKey, compound components (Header, Messages, Footer, Input)

```tsx
<AIContainer messages={messages}>
  <AIContainer.Messages emptyContent={<AIEmptyState title="Hi!" />} />
  <AIContainer.Input inputProps={{ value, onChange, onSubmit }} />
</AIContainer>
```

```tsx
// Use one autoScrollKey owner when the transcript is rendered as custom children.
// Auto-scroll pauses while the user reads older messages and resumes at bottom.
<AIContainer autoScrollKey={messages.at(-1)?.id ?? null}>
  <AIContainer.Messages>
    {messages.map((message) => (
      <CustomMessageRow key={message.id} message={message} />
    ))}
  </AIContainer.Messages>
</AIContainer>
```

Place `autoScrollKey` on `AIContainer.Messages` instead when only that
message region owns the transcript state. Do not pass both for the same list.

### AIContextIndicator
Controlled AI conversation-context lifecycle message with full, compacting, and compacted states, localizable copy, and consumer-controlled compaction progress

### AIEmptyState
Welcome state with suggestions

### AIFeedbackBar
Thumbs up/down rating

Props: value, onChange, variant (default|subtle|inline), size (sm|md|lg)

```tsx
<AIFeedbackBar value={feedback} onChange={setFeedback} />
```

### AIForm
Schema-driven form block for collecting structured input inside AI responses

### AIInput
Chat input with customizable action slots, native drag-and-drop file upload, paste-to-file conversion (large/structured paste auto-converts to attachment)

Props: variant (default|compact|inline), value, onChange, onSubmit, placeholder, disabled, uploadingFiles, onRemoveFile, onFilesSelected, accept, multiple, dropText, pasteAsFile

**AIInput shell parity:** The convenience `<AIInput>` path and compound `<AIInput.Root>` path share the Figma shell treatment. Default mode uses the rounded `max-w-[850px]` shell, flat primary focus/text/drag border, token-backed shadow, and no legacy gradient wrapper. `AIInput.ActionButton` and `AIInput.AttachButton` icons use `text-secondary-foreground`.

**Drag-drop file upload:** provide `onFilesSelected` to enable. Gradient border + dashed overlay on drag-over. AttachButton auto-wires to file picker via context (custom `onClick` overrides). Reuses `useDropZone` internally; respects `accept` and `multiple`.

**Paste-to-file conversion:** set `pasteAsFile` (boolean or config). Large pastes (>500 chars OR >10 lines) and structured content (JSON, XML/HTML, CSV, code, log/stack-trace) auto-convert to a synthesized File and route through `onFilesSelected`. Filename: `Pasted-N.{ext}` where ext is detected (json, xml, csv, log, txt). Inline variant ignores the prop. Respects `accept` (mismatch falls through to native paste). React-only — not exposed to Web Component bridge because callbacks can't cross HTML attributes.

Optional config object: `{ threshold, lineThreshold, detectStructured, prefillTemplate, onConverted }`. `prefillTemplate(filename, kind) => string` auto-fills the textarea after conversion (appended with leading space if textarea non-empty); empty/whitespace return is a no-op. `onConverted(filename, kind)` fires after `onFilesSelected` and prefill — useful for analytics or toasts.

Detection helpers exported from package main: `shouldConvertPaste`, `detectPasteKind`, `analyzePaste`, `mapKindToFile`, `KIND_TO_FILE` plus types `PasteKind`, `PasteAsFileConfig`, `PasteAsFileProp`, `DetectionOpts`, `PasteAnalysis`. Useful for consumers needing detection without AIInput.

```tsx
// Drag-drop only
<AIInput
  onFilesSelected={handleFiles}
  accept="image/*,.pdf"
  uploadingFiles={files}
  onRemoveFile={handleRemove}
  onSubmit={handleSubmit}
/>

// Drag-drop + paste-to-file (zero-config)
<AIInput
  onFilesSelected={handleFiles}
  uploadingFiles={files}
  onRemoveFile={handleRemove}
  onSubmit={handleSubmit}
  pasteAsFile
/>

// Drag-drop + paste-to-file with prompt prefill
<AIInput
  onFilesSelected={handleFiles}
  uploadingFiles={files}
  onSubmit={handleSubmit}
  pasteAsFile={{
    prefillTemplate: (name, kind) =>
      kind === 'csv' ? `Summarize ${name}` : `Analyze ${name}`,
    onConverted: (name, kind) => track('paste-as-file', { kind }),
  }}
/>
```

### AIMermaidDiagram
Renders Mermaid diagrams

### AIMessage
Chat bubble (sent/received/agent) with avatar, markdown, reactions

Props: type (sent|received), content, markdown, avatar, isAgent, showActions, senderName

```tsx
<AIMessage type="received" content="Hello!" senderName="AI" isAgent />
```

### AIPromptSuggestion
Clickable prompt cards

### AIReasoningBlock
Collapsible chain-of-thought display

Props: children, title, open, defaultOpen, isStreaming, markdown, variant (default|thinking|subtle)

```tsx
<AIReasoningBlock title="Thinking..." isStreaming>{reasoningText}</AIReasoningBlock>
```

### AIResponseStream
Animated text streaming (typewriter/fade)

### AIScrollButton
Floating scroll-to-bottom

### AISelect
Schema-driven single-select block for interactive AI responses

### AISource
Citation with favicon, title, URL

### AISteps
Multi-step AI progress with status icons, timing, expandable details

### AISystemMessage
System/status messages (error, warning, info)

### AITable
Schema-driven data table block for AI responses with selection and empty states

### AITextShimmer
Loading text effects (shimmer, pulse, typing)

### AIThinkingLoader
Processing indicator with progress circles

### AIToolCall
Tool/function call display with status

### AIToolRun
Validated AI tool-run timeline with lifecycle, progress, sources, disclosure, and actions

### AITypingIndicator
Typing dots animation

## Content

### ActivityFeed
Activity feed with divider styles

### DataTable
TanStack Table with sorting, filtering, pagination, selection

Props: columns (ColumnDef[]), data, getRowId (recommended), enableSorting, enablePagination, pageSize, paginationType, paginationShape, paginationSize (xs|sm|md|lg), enableRowSelection, responsiveColumns with column.meta.responsive, dividers (line|alternating), density (default|compact)

Responsive columns: opt in with responsiveColumns and set column.meta.responsive = { priority?: 'always'|'desktop'|'mobile', hideBelow?: 'sm'|'md'|'lg' }. Omitted priority/hideBelow defaults to desktop columns hidden below md; priorities 'always' and 'mobile' ignore hideBelow.

```tsx
<DataTable columns={columns} data={rows} getRowId={(r) => r.id} enableSorting enablePagination />
```

### SortableHeader
DataTable column header control that reflects and changes TanStack sorting state

### EmptyState
Product empty state with title, description, optional actions, centered featured icon, illustration or file type media, and decorative background patterns

Props: title, description, size (sm|md|lg), media (featured-icon|illustration|file-type-icon|none), pattern (auto|circles|grid|grid-dot|squares|none), icon, iconLabel, illustrationVariant (cloud|box|documents|credit-card), illustrationTone (primary|gray), fileExtension, fileType, primaryAction, secondaryAction, actions, headingLevel

Use for product empty states in lists, tables, panels, uploads, search/filter zero-results, and first-run workspace sections. Prefer `EmptyState` for non-chat product empty states. Keep `AIEmptyState` for chat welcome states and prompt suggestions.

```tsx
<EmptyState
  title="No results found"
  description="Try adjusting your search terms or start fresh with a new search."
  media="featured-icon"
  icon={<Search />}
  primaryAction={{
    label: 'New search',
    startIcon: <Plus />,
    onClick: handleNewSearch,
  }}
  secondaryAction={{ label: 'Clear search', onClick: clearSearch }}
/>

<EmptyState
  title="No files yet"
  description="Upload a document or create a folder to get started."
  media="file-type-icon"
  fileExtension="pdf"
  pattern="circles"
/>
```

### GroupingControls
Row grouping controls for DataTable

### History
Chronological audit history with categorized events, actor metadata, value changes, comments, and loading states

### InlineCTA
CTA card (actions, email, image)

### MetricCard
Metric display card

Props: value (required), title, change, changeSentiment (positive|negative|neutral), data, series, chartType (line|bar|area), valueFormatter

```tsx
<MetricCard title="Revenue" value={52000} change={18.5} changeSentiment="positive" />
```

### Chart color contract

Prefer HUMAIN chart components for generated output. They keep sizing, legends, and token usage aligned with the design system.

When using `ChartContainer` or Recharts primitives directly:

- Provide a config object with one entry per labeled series.
- Each entry needs `label` plus `color: 'var(--chart-N)'` or a valid semantic token.
- Set `fill` or `stroke` on raw Recharts series with the same token-backed colors.
- Do not rely on default Recharts colors.

```tsx
const chartConfig = {
  approvals: { label: 'Approvals', color: 'var(--chart-1)' },
  rejections: { label: 'Rejections', color: 'var(--chart-2)' },
};
```

### MetricItem
KPI display with value, label, change indicator, sparkline

### NotificationPanel
Notification center with grouped sections

### Steps
Wizard-style step indicator (horizontal/vertical, compound API)

## Layout

### PageHeader
Header with breadcrumbs, title, tabs, actions

Props: variant (simple|avatar|banner-*), title, supportingText, breadcrumbs, actions, showDivider

```tsx
<PageHeader title="Dashboard" supportingText="Welcome back!" actions={[{ label: 'New', variant: 'primary' }]} />
```

### SectionHeader
Section-level header with title, supporting text, configurable heading level, search, optional search filter control, grouped controls, actions, scrollable tabs, optional menuButton control, and divider

Props: title, supportingText, size (sm|md), headingLevel (1-6), actions, toggleGroup, search, search.filterButton, tabs, menuButton, showDivider

Use for section-level page regions. Grouped selection controls compose through ToggleGroup, tabs compose through Tabs, long labels wrap/scroll safely, and interactive icon controls should be passed through search.filterButton or the opt-in menuButton prop.

```tsx
<SectionHeader
  title="Team members"
  headingLevel={3}
  supportingText="Manage permissions"
  search={{ placeholder: 'Search', ariaLabel: 'Search team members' }}
  toggleGroup={{
    'aria-label': 'Member status',
    defaultValue: ['active'],
    items: [{ label: 'Active', value: 'active' }, { label: 'Pending', value: 'pending' }],
  }}
  actions={[{ label: 'Invite', appearance: 'solid', variant: 'primary' }]}
  tabs={[{ label: 'Overview', value: 'overview' }, { label: 'Activity', value: 'activity' }]}
/>
```

## Menus

### CommandMenu
Cmd+K palette with search

### ContextMenu
Right-click context menu

### DropdownMenu
Context menu with items, groups, shortcuts

Compound API: DropdownMenu, DropdownMenu.Trigger, DropdownMenu.Popup, DropdownMenu.Item, DropdownMenu.Separator
Props (DropdownMenu.Popup): width (auto|sm|md|lg), side, align
Props (DropdownMenu.Item): icon, shortcut, destructive

```tsx
<DropdownMenu>
  <DropdownMenu.Trigger render={<Button>Menu</Button>} />
  <DropdownMenu.Popup width="md">
    <DropdownMenu.Item icon={<Settings />}>Settings</DropdownMenu.Item>
    <DropdownMenu.Separator />
    <DropdownMenu.Item destructive>Delete</DropdownMenu.Item>
  </DropdownMenu.Popup>
</DropdownMenu>
```

## Overlays

### AlertDialog
Confirmation dialog

### Dialog
Modal with header, body, footer, icon

Compound API: Dialog, Dialog.Trigger, Dialog.Popup, Dialog.Header, Dialog.Title, Dialog.Description, Dialog.Body, Dialog.Footer, Dialog.Action, Dialog.Cancel, Dialog.Icon, Dialog.Close
Props (Dialog): open, onOpenChange, defaultOpen, modal
Props (Dialog.Popup): size (sm|md|lg|xl|full), showCloseButton

```tsx
<Dialog>
  <Dialog.Trigger render={<Button />}>Open</Dialog.Trigger>
  <Dialog.Popup>
    <Dialog.Header>
      <Dialog.Title>Title</Dialog.Title>
      <Dialog.Description>Description</Dialog.Description>
    </Dialog.Header>
    <Dialog.Body>Content</Dialog.Body>
    <Dialog.Footer>
      <Dialog.Cancel>Cancel</Dialog.Cancel>
      <Dialog.Action>Confirm</Dialog.Action>
    </Dialog.Footer>
  </Dialog.Popup>
</Dialog>
```

### Drawer
Slide-out panel

Compound API: Drawer, Drawer.Trigger, Drawer.Popup, Drawer.Header, Drawer.Title, Drawer.Footer, Drawer.Close
Props: direction (top|right|bottom|left), open, onOpenChange

```tsx
<Drawer direction="right">
  <Drawer.Trigger render={<Button />}>Open</Drawer.Trigger>
  <Drawer.Popup>
    <Drawer.Header><Drawer.Title>Panel</Drawer.Title></Drawer.Header>
    <div className="p-4">Content</div>
  </Drawer.Popup>
</Drawer>
```

### HoverCard
Rich hover tooltip

### Popover
Floating content panel

Components: Popover, PopoverPopup, PopoverHeader, PopoverTitle
Props: trigger, open, onOpenChange
Props (PopoverPopup): side, align

```tsx
<Popover trigger={<Button>Open</Button>}>
  <PopoverPopup>Popover body</PopoverPopup>
</Popover>
```

### Sheet
Side sheet with sections

Components: Sheet, SheetPopup, SheetHeader, SheetTitle, SheetBody, SheetFooter, SheetClose
Props (SheetPopup): side (top|right|bottom|left), width (sm|md|lg|xl|full)

```tsx
<Sheet trigger={<Button>Open</Button>}>
  <SheetPopup side="right" width="md">
    <SheetHeader><SheetTitle>Panel</SheetTitle></SheetHeader>
    <SheetBody>Content</SheetBody>
  </SheetPopup>
</Sheet>
```

### Tooltip
Simple text tooltip

Components: Tooltip, TooltipTrigger, TooltipContent
Props (TooltipContent): side (top|right|bottom|left), sideOffset

```tsx
<Tooltip>
  <TooltipTrigger><Button>Hover me</Button></TooltipTrigger>
  <TooltipContent side="top">Tooltip text</TooltipContent>
</Tooltip>
```
