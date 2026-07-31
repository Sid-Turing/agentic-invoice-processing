# Molecules

Compose atoms into functional units.

## Charts

### AreaChart
Filled time series with overlaid or stacked series

Props: data, series, areaMode (overlaid|stacked|expanded), fillStyle (solid|gradient), curveType (linear|smooth|step), size (sm|default|lg|xl), showYAxis, showXAxis, legendPosition (none|top|bottom|right)

Default palette: `[--chart-1, --chart-2, --chart-3, --chart-4, --chart-5]`. Override via `series.color`.

```tsx
<AreaChart
  data={data}
  series={[{ id: 'visitors', label: 'Visitors' }]}
  fillStyle="gradient"
/>
```

### BarChart
Vertical bars (grouped/stacked)

Props: data, series, barMode (stacked|grouped), size (sm|default|lg|xl), showYAxis, showXAxis, legendPosition (none|top|right)

Default palette — stacked: `[--slate-500, --chart-2, --chart-1]` (neutral baseline, then primary stack). Grouped: full categorical `[--chart-1..5]`. Override per series via `series.color` (any CSS color).

```tsx
<BarChart data={data} series={[
  { id: 'a', label: 'A' },                          // → --slate-500 (stacked) / --chart-1 (grouped)
  { id: 'b', label: 'B', color: 'var(--green-500)' }, // explicit override
]} barMode="grouped" showYAxis showXAxis />
```

### ChartCard
Card wrapper for chart titles, context, plot content, alignment, and directional trend summaries

Props: title (required), label, kind (area|bar|line|pie|radar|radial), description, trend, trendDirection (up|down|flat), footerDescription, align (start|center), plotClassName, children, plus Card size/padding props

Set `trendDirection` when a trend icon communicates direction. Omitting it keeps a text-only trend instead of implying an upward result.

```tsx
<ChartCard
  label="Revenue"
  kind="line"
  title="$148K"
  description="Last 30 days"
  trend="12% from last month"
  trendDirection="up"
>
  <LineChart data={data} series={series} />
</ChartCard>
```

### DonutChart
Donut chart

Props: data, series, centerValue, centerLabel, size (xs|sm|md|lg), legendPosition (none|bottom|right)

Default palette: `[--chart-1, --chart-2, --chart-3]`. Donut data points may set `color` to override.

```tsx
<DonutChart data={data} series={series} centerValue="85%" centerLabel="Score" />
```

### HorizontalBarChart
Horizontal bars

Props: data, barColor (default `var(--chart-1)`), valueFormatter, size (sm|default|lg)

Single-color bar list. Override globally via `barColor` or per-bar via `data[i].color`.

```tsx
<HorizontalBarChart data={data} barColor="var(--chart-2)" />
```

### LineChart
Time series with multiple series

Props: data, series, size (sm|default|lg|xl), showYAxis, showXAxis, legendPosition (none|top|right)

Default palette: `[--chart-1, --chart-2, --chart-3, --chart-4, --chart-5]` — categorical, mode-aware. Override via `series.color`.

```tsx
<LineChart data={data} series={[
  { id: 'rev', label: 'Revenue' },                              // → --chart-1
  { id: 'cost', label: 'Cost', color: 'var(--destructive)' },    // semantic override
]} showYAxis showXAxis />
```

Use CSS variables for overrides so theme retargeting remains token-backed. Do not import lower-level chart primitives from the package root unless they are explicitly exported.

### PieChart
Pie chart

Props: data, series, size (sm|default|lg|xl), legendPosition (none|bottom|right)

Default palette: `[--chart-1..5, --slate-500]` — last slot is the neutral baseline for "other" categories. Override per data point via `d.color`.

```tsx
<PieChart data={data} series={series} legendPosition="right" />
```

### RadarChart
Multi-dimensional comparison

Props: data, series, size (sm|default|lg|xl), legendPosition (none|top|right)

Default palette: same as LineChart (`[--chart-1..5]`). Override per series via `series.color`.

```tsx
<RadarChart data={data} series={series} />
```

### RadialChart
Concentric progress rings and gauges

Props: data, series, shape (circle|gauge), maxValue, centerValue, centerLabel, size (xs|sm|md|lg), legendPosition (none|bottom|right), showGrid

Default palette: `[--chart-1..5]`. Override per data item via `color`.

```tsx
<RadialChart
  data={[{ id: 'score', label: 'Score', value: 72 }]}
  centerValue={72}
  centerLabel="Score"
/>
```

## Data

### Avatar
User avatar with fallback, status

Props: src, alt, fallback, size (xs|sm|md|lg|xl|2xl), status

```tsx
<Avatar src="/avatar.png" alt="User" fallback="JD" size="md" />
```

### BrandIcon
HUMAIN brand mark, symbol, wordmark, and combined logo renderer with responsive sizing and accessible labels

### Calendar
Full calendar (month/week/day) with events

Props: view (month|week|day), onViewChange, selectedDate, onDateSelect, events, onEventClick

```tsx
<Calendar view="month" events={events} onDateSelect={setDate} />
```

### CodeSnippet
Syntax-highlighted code with line numbers

### DatePicker
Date input with calendar popup, range support

Props: value, onChange, placeholder, dateFormat, minDate, maxDate, disabled

```tsx
<DatePicker value={date} onChange={setDate} placeholder="Pick a date" />
```

### FeaturedIcon
Styled icon container with size (xs-lg), shape (rounded/round), and color variants

### Item
Composable list item with title, description, leading/trailing slots, variants, sizes, groups, and polymorphic rendering

### Kbd
Keyboard shortcut display (platform-aware)

### Table
Basic table

## Feedback

### Alert
Inline feedback message with outline, solid, and soft appearances; semantic variants; actions; and dismissal

### Sonner
Toast notification system

## Files

### FileTypeIcon
File extension icon display

### FileUpload
Figma upload shell with drag-drop, URL upload, stateful progress, and card/stack/list file views. Uses `useDropZone` internally.

Components: FileUpload, FileUploadArea, FileUploadItem
Props: files, onFilesSelected, onFileRemove, onFileCancel, onFileRetry, areaProps, helpText, fileView (default|stack|list), uploadFromUrl, uploadUrl, onUrlUpload, selectedFileIds, onSelectedFileIdsChange, onFilesDownload

FileUpload derives the Figma default, uploading, error, complete, and many-file shells from `files`. Use `uploadFromUrl` for the optional URL form and `fileView` for uploaded-file presentation.

FileUploadItem uses the Figma FileMiniCard as its only design. Use `mobile` for the 100x100 compact card and `showProgress={false}` for available files whose metadata should show size only; do not pass the removed `progressType` variants.

```tsx
<FileUpload
  files={files}
  onFilesSelected={setFiles}
  onFileRemove={handleRemove}
  onFileRetry={handleRetry}
  uploadFromUrl
  onUrlUpload={handleUrlUpload}
  fileView="default"
/>
```

```tsx
<FileUploadItem fileName="Report.pdf" fileSize="200 KB" fileExtension="pdf" progress={70} status="uploading" onCancel={handleCancel} />
<FileUploadItem mobile fileName="Report.pdf" fileExtension="pdf" progress={0} status="error" onRetry={handleRetry} />
```

### useDropZone (hook)
Reusable drag-drop behavior hook. Handles drag counter, accept filtering, multiple enforcement, file picker.

```tsx
import { useDropZone } from '@humain/ui';

const { isDragging, dropZoneProps, openFilePicker } = useDropZone({
  onFilesSelected: handleFiles,
  accept: 'image/*',
  multiple: true,
});

<div {...dropZoneProps}>Drop zone content</div>
```

## Forms

### AdvancedRating
Figma-aligned 0-5 rating compositions using emoji, icons, numbers, sliders, badges, and controlled state

### Autocomplete
Autocomplete input with multi-select. Accepts field props for auto Field wrapping

### ComboboxMenu
Autocomplete with keyboard nav

### DisplayValue
Read-only label/value display

### Field
Form field wrapper with label, hint, error

### Form
Form container with validation

### InputGroup
Compound input shell with shared sizing, shape, validation, fill, disabled/read-only state, addons, text, textarea, and attached buttons

Compound API: InputGroup, InputGroupInput, InputGroupTextarea, InputGroupAddon, InputGroupText, InputGroupButton
Props (InputGroup): size (xs|sm|md|lg), shape (rounded|round), state (default|success|destructive), filled, disabled, readOnly
Props (InputGroupAddon): align (inline-start|inline-end|block-start|block-end)
Props (InputGroupButton): Button props plus flush for an attached edge-to-edge action

Group size, validation state, disabled, and read-only behavior propagate to descendant controls. Use InputGroup for one compound field; keep independent fields as separate Input components.

```tsx
<InputGroup aria-label="Website">
  <InputGroupAddon align="inline-start">
    <InputGroupText>https://</InputGroupText>
  </InputGroupAddon>
  <InputGroupInput aria-label="Website address" placeholder="example" />
  <InputGroupAddon align="inline-end">
    <InputGroupText>.com</InputGroupText>
  </InputGroupAddon>
</InputGroup>

<InputGroup aria-label="Invite by email">
  <InputGroupInput aria-label="Email address" placeholder="name@company.com" />
  <InputGroupButton flush appearance="solid" variant="primary">Invite</InputGroupButton>
</InputGroup>
```

### InputOTP
One-time password input

### RichTextarea
Rich text editor with formatting toolbar

## Navigation

### Accordion
Collapsible sections

Components: Accordion, AccordionItem, AccordionTrigger, AccordionContent

```tsx
<Accordion>
  <AccordionItem value="item-1">
    <AccordionTrigger>Section 1</AccordionTrigger>
    <AccordionContent>Content</AccordionContent>
  </AccordionItem>
</Accordion>
```

### Breadcrumb
Navigation breadcrumbs

Components: Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbLink, BreadcrumbPage
Props (Breadcrumb): separator (chevron|slash), ring
Props (BreadcrumbLink/BreadcrumbPage): variant (text|soft-badge|outline-badge)

```tsx
<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem><BreadcrumbLink href="/">Home</BreadcrumbLink></BreadcrumbItem>
    <BreadcrumbItem><BreadcrumbPage>Current</BreadcrumbPage></BreadcrumbItem>
  </BreadcrumbList>
</Breadcrumb>
```

### Carousel
Controlled or uncontrolled horizontal/vertical carousel with multiple content layouts, navigation styles, keyboard, pointer, and touch support

### Collapsible
Collapsible content section

### Pagination
Page navigation

Props: type (page-default|page-minimal|card-default|card-minimal|card-button-group), shape (square|circle), currentPage, totalPages, onPageChange, showPageNumbers

```tsx
<Pagination currentPage={1} totalPages={10} onPageChange={setPage} />
```

### Tabs
Tab navigation (underline, pills, button variants); horizontal or vertical orientation

Components: Tabs, TabsList, TabsTrigger, TabsContent, TabsIndicator
Props (Tabs): value, defaultValue, onValueChange, orientation (horizontal|vertical, default horizontal)
Props (TabsList): variant (boxed|pill|bordered|lifted), align (start|center|end|stretch)

`orientation="vertical"` flips the layout from column to row — list renders alongside content instead of stacked above it. The DOM exposes `data-orientation` on the root for any custom styling. Keyboard arrow nav follows orientation.

```tsx
// Horizontal (default)
<Tabs defaultValue="tab1">
  <TabsList variant="bordered">
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
    <TabsIndicator />
  </TabsList>
  <TabsContent value="tab1">Content 1</TabsContent>
</Tabs>

// Vertical — list on the side, content adjacent
<Tabs defaultValue="account" orientation="vertical">
  <TabsList>
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="security">Security</TabsTrigger>
    <TabsTrigger value="billing">Billing</TabsTrigger>
  </TabsList>
  <TabsContent value="account">Account settings</TabsContent>
  <TabsContent value="security">Security settings</TabsContent>
  <TabsContent value="billing">Billing settings</TabsContent>
</Tabs>
```
