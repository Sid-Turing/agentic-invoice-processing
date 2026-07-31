# Atoms

Single-element building blocks.

## Buttons

### Button
Action button with two axes: appearance (solid, outline, ghost, link, soft, gradient, ai) and variant (primary, secondary, info, success, warning, destructive). shape controls border-radius (rounded=md, round=full-pill).

Props: appearance (solid|gradient|soft|outline|ghost|link|ai), variant (primary|secondary|info|success|warning|destructive), shape (rounded|round), size (default|xs|sm|md|lg|xl|2xl|icon|icon-xs|icon-sm|icon-lg|icon-xl|icon-2xl), render, loading, startIcon, endIcon, iconOnly, animated

Defaults: appearance="solid", variant="primary", shape="rounded", size="default"
Default shape="rounded" produces standard rectangular buttons (rounded-md). Use shape="round" for pill-shaped buttons (rounded-full).

```tsx
<Button appearance="solid" variant="primary" shape="rounded" size="md">Submit</Button>
<Button appearance="outline" variant="secondary" shape="rounded" render={<a href="/home" />}>Go Home</Button>
<Button appearance="ghost" variant="primary" size="icon"><Search className="size-4" /></Button>
```

### Toggle
Toggle button; also exports ToggleGroup and ToggleGroupItem for grouped selection

## Display

### Badge
Status badge (gray, brand, error, warning, success)

Props: color (primary|secondary|info|success|warning|destructive), variant (solid|soft|outline|white|dot), size (xs|sm|md|lg), shape (round|rounded)

```tsx
<Badge variant="dot" color="success" size="sm">Active</Badge>
<Badge variant="white" color="primary" size="sm">Overlay</Badge>
```

### LoadingIndicator
Loading spinners

### Progress
Linear or circular progress indicator

Props: value (0-100), size (sm|md|lg|xl), color, circular, showValue

```tsx
<Progress value={75} />
<Progress circular value={60} size="md" showValue />
```

### Rating
Interactive or read-only star/heart rating with half-value display, semantic colors, and sm-lg sizes

### Skeleton
Loading placeholder

### SparklineChart
Compact line or area trend chart with token colors, smooth/linear curves, and accessible labeling

## Forms

### Checkbox
Checkbox with variants and sizes. Accepts field props (label, error) for auto inline Field wrapping

Props: variant (primary|secondary|info|success|warning|destructive), size (sm|md|lg), checked, onCheckedChange, indeterminate
Field props: label, error, description, tooltip, fieldClassName

```tsx
<Checkbox checked={agreed} onCheckedChange={setAgreed} />
<Checkbox label="Accept terms" error={errors.agreed} />
```

### CheckboxGroup
Checkbox group with card layout, featured icons

### FileInput
Single-file picker with xs-lg sizes, controlled/uncontrolled value, validation, disabled, and read-only states

Props: size (xs|sm|md|lg), success, disabled, readOnly, value, defaultValue, onChange, accept, placeholder, browseLabel, browseIcon, deleteLabel, deleteIcon
Field props: label, error, description, tooltip, required, fieldClassName

`readOnly` displays the selected filename on a muted surface without browse or delete actions. Use `value`/`onChange` for controlled state or `defaultValue` for uncontrolled state.

```tsx
<FileInput label="Evidence" accept=".pdf,image/*" onChange={setFile} />
<FileInput value={file} onChange={setFile} readOnly />
```

### Input
Text input with size variants, icons, addons. Accepts field props (label, error, description) for auto Field wrapping

Props: size (sm|md|lg), state (default|success|destructive), startIcon, endIcon, startAddon, endAddon
Field props: label, error, description, tooltip, required, fieldClassName

```tsx
<Input size="md" placeholder="Enter email" />
<Input label="Email" error={errors.email} placeholder="name@co.com" required />
<Input state="destructive" placeholder="Invalid input" />
```

### NumberInput
Numeric field with five stepper layouts, sm-lg sizes, controlled/uncontrolled value, range limits, and validation states

Props: variant (default|verticalButtons|horizontalButtons|stretchedButtons|mini), size (sm|md|lg), state (default|success|destructive), destructive, value, defaultValue, onChange, min, max, step, disabled, readOnly
Field props: label, error, description, tooltip, required, fieldClassName

```tsx
<NumberInput label="Seats" min={1} max={20} defaultValue={4} />
<NumberInput variant="mini" value={quantity} onChange={setQuantity} />
<NumberInput state="destructive" error="Enter a supported quantity" />
```

### RadioGroup
Radio group

### Select
Dropdown select with flat API. Accepts field props for auto Field wrapping. Use SelectRoot for compound API

Flat API: placeholder, size (xs|sm|md|lg), shape (rounded|round), readOnly
Field props: label, error, description, tooltip, topRight, bottomRight, fieldClassName
Use the flat `Select` API for normal fields and filters. Its popup anchors below/above the trigger by default; do not opt into selected-item overlap.

```tsx
<Select placeholder="Select..." value={value} onValueChange={setValue}>
  <SelectItem value="opt1">Option 1</SelectItem>
</Select>

<Select label="Role" error={errors.role} placeholder="Select a role">
  <SelectItem value="dev">Developer</SelectItem>
</Select>
```

For compound/custom triggers, use SelectRoot:
```tsx
<SelectRoot value={value} onValueChange={setValue}>
  <SelectTrigger><SelectValue placeholder="Select..." /></SelectTrigger>
  <SelectPopup alignItemWithTrigger={false} side="bottom" sideOffset={4}><SelectItem value="opt1">Option 1</SelectItem></SelectPopup>
</SelectRoot>
```

### SelectItem
Selectable option for flat or compound Select composition

### Slider
Range slider with single/dual handles, vertical orientation, semantic colors, and Figma-aligned advanced compositions.

Props: mode (single|range), variant (default|with-sub-label|with-numbers|radio|with-percentages|with-icon|with-icon-and-number|with-badge|with-badge-range|rounded-avatar|square-avatar|simple-line|gradient|emojis), value, onValueChange, min, max, orientation (horizontal|vertical), size (sm|md|lg), color (primary|info|success|warning|error), label, labelMode (none|bottom|floating), valueFormat, getAriaValueText, marks, startContent, endContent, thumbContent

```tsx
<Slider mode="single" value={[50]} onValueChange={setVal} min={0} max={100} />
<Slider variant="radio" marks={scoreMarks} />
<Slider variant="with-badge-range" defaultValue={[25, 75]} startContent="$25" endContent="$99" />
```

### Switch
Toggle switch. Accepts field props (label, description) for auto inline Field wrapping. Use theme-gradient, theme-switch, theme-pill, or theme-segmented variants for light/dark controls.

Props: variant (primary|secondary|warning|info|success|destructive|theme-gradient|theme-switch|theme-pill|theme-segmented), size (sm|md|lg), checked, onCheckedChange
Field props: label, description, tooltip, fieldClassName

```tsx
<Switch checked={on} onCheckedChange={setOn} />
<Switch label="Enable notifications" description="Get email alerts" />
<Switch variant="theme-segmented" />
```

### Textarea
Multi-line input. Accepts field props (label, error, description) for auto Field wrapping

Props: state (default|success|destructive), startIcon, endIcon, hasOutline
Field props: label, error, description, tooltip, required, fieldClassName

```tsx
<Textarea placeholder="Type here..." />
<Textarea label="Message" description="Max 500 chars" />
<Textarea state="destructive" placeholder="Explain the issue" />
```

## Layout

### AccordionCard
Card with expandable content

### Card
Container with header, content, footer

Compound API: Card, Card.Header, Card.Title, Card.Description, Card.Action, Card.Content, Card.Footer
Props: size (default|sm), padding (none|md)
Props (Card.Content): padding (none|md)
Defaults: padding="md" on Card and Card.Content. Use padding="none" for edge-to-edge media, charts, or custom table chrome.

```tsx
<Card>
  <Card.Header><Card.Title>Title</Card.Title></Card.Header>
  <Card.Content>Body</Card.Content>
  <Card.Footer>Footer</Card.Footer>
</Card>
```

### Resizable
Resizable panel layout

### ScrollArea
Custom scrollbars

### Separator
Visual separator supporting single-line, dual-line, and background-fill Figma treatments with optional text, heading, or custom center content

Props: appearance (single|dual|filled), orientation (horizontal|vertical), label, labelVariant (text|heading), children

Defaults: appearance="single", orientation="horizontal", labelVariant="text"

Use `label` for accessible text separators. Use `children` for centered content such as `Button` or `ToggleGroup`; the wrapper intentionally does not set `role="separator"` around interactive children.

```tsx
<Separator />
<Separator label="Today" />
<Separator appearance="dual" label="Notifications" labelVariant="heading" />
<Separator appearance="filled" label="Today" />

<Separator>
  <Button size="sm">Add</Button>
</Separator>
```

## Workflow

### WorkflowAddNode
Workflow insertion control with accessible add actions, hover actions, keyboard support, and disabled state

### WorkflowCircleNode
Circular workflow node with kind, status, selection, icon, and compact visual variants

### WorkflowComment
Workflow annotation node with author metadata, layout, execution, selection, and disabled states

### WorkflowConnection
Workflow edge with direction, status, label, selection, hover actions, and accessibility metadata

### WorkflowNode
General workflow node with kind, size, layout, status, selection, ports, actions, and disabled state

### WorkflowPort
Accessible workflow connection port with input/output kinds, statuses, labels, and control placement
