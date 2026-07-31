# Design Excellence Standards

Checklists for color, typography, spacing, responsiveness, hardening, polish in `@humain/ui` components.

---

## 1. Color & Theming

### Semantic Token Usage

Always use semantic tokens — never raw hex or Tailwind palette colors directly.

**Text hierarchy:**

| Token | Use |
|-------|-----|
| `text-foreground` | Primary body text, headings |
| `text-secondary-foreground` | Secondary custom copy, labels, table cells |
| `text-muted-foreground` | Icons, placeholders, decorative metadata only |
| `text-text-quaternary` | Disabled text, faintest labels |
| `text-destructive` | Error messages, danger labels |
| `text-warning` | Warning messages |
| `text-success` | Success messages, confirmation labels |
| `text-info` | Informational messages, hints |

Use `text-secondary-foreground` for readable custom body copy, table cells, timestamps, captions, and instructional text you write directly. Component-provided `Description` and `Subtitle` parts may keep their built-in token defaults. Do not use direct `text-muted-foreground` utilities for paragraphs, table cells, timestamps, captions, or instructional copy.

**Surface hierarchy (use in order, never skip levels):**

| Token | Context | Light | Dark |
|-------|---------|-------|------|
| `bg-app` | Default app/product canvas | `var(--app-background)` | `var(--app-background)` |
| `bg-background` | Intentional solid surface | `#ffffff` | `#161616` |
| `bg-card` | Cards, modals, sheets | `#ffffff` | `#ffffff05` (semi-transparent) |
| `bg-popover` | Dropdowns, tooltips, menus | `#fffffff2` | `#000000f2` |
| `bg-muted` | Subtle/disabled areas, skeletons | `#00000005` | `#ffffff05` |
| `bg-surface-1` | First nested section | `#fafafa` | `#07090c` |
| `bg-surface-2` | Second nested section | `#f5f5f5` | `#121212` |
| `bg-surface-3` | Third nested section | `#eeeeee` | `#1f1f1f` |
| `bg-accent` | Hover, selected row/item | `#f5f5f5` | `#404040` |

Default app/product screens use `bg-app` through `AppShell.Root`. Do not use wrapper `bg-background` or `background="var(--background)"` unless the page deliberately needs a flat solid canvas.

**Brand colors:**

- Primary: `bg-primary` (#009688, Humain aqua) — CTAs, active states, badges
- Air scale: `air-50` (lightest) through `air-950` (darkest)
- Secondary palettes: `air-*`, `oasis-*`, `slate-*`

**Chart colors (use in order for multi-series):**

| Token | Hex | Use |
|-------|-----|-----|
| `chart-1` | `#009688` | Primary series |
| `chart-2` | `#2ecab1` | Secondary series |
| `chart-3` | `#7fae14` | Tertiary series |
| `chart-4` | `#b8e636` | Fourth series |
| `chart-5` | `#e1f88a` | Fifth series |

For generated charts, prefer HUMAIN chart wrappers (`BarChart`, `LineChart`, `DonutChart`, `PieChart`, `RadarChart`, `MetricCard` sparkline support). If you use `ChartContainer` or raw Recharts primitives, every labeled series must have token-backed color:

```tsx
const chartConfig = {
  revenue: { label: 'Revenue', color: 'var(--chart-1)' },
  target: { label: 'Target', color: 'var(--chart-2)' },
};
```

Do not use raw hex values, Tailwind palette names, browser defaults, or unlabeled config entries for chart series.

**Sidebar-specific tokens (only within AppSidebar):**

`sidebar` (bg), `sidebar-foreground`, `sidebar-primary`, `sidebar-accent`, `sidebar-border`

**Border tokens:**

`border-border` (default), `border-primary` (focus/active), `border-destructive` (error state)

### Dark Mode Checklist

- [ ] Test every new surface with `ThemeProvider defaultTheme="dark"` — `bg-card` becomes semi-transparent, verify contrast
- [ ] Never use `dark:` Tailwind modifier manually — tokens auto-switch
- [ ] Use `bg-popover` (not `bg-card`) for floating layers — maintains opacity in dark mode
- [ ] Verify status colors (`text-destructive`, `text-warning`, `text-success`) legible in both modes

---

## 2. Typography

### Font Setup

Tokens prefer Inter through `--font-family`; host apps must load Inter or accept the system fallback. Avoid duplicate font loading when the host already provides it.

```tsx
import { ThemeProvider } from '@humain/ui'

<ThemeProvider>
  <App />
</ThemeProvider>
```

### Type Scale

**Display scale** — headings, hero text, marketing copy:

| Class | Size | Use |
|-------|------|-----|
| `text-display-2xl` | 72px | Hero/landing titles |
| `text-display-xl` | 60px | Page hero headings |
| `text-display-lg` | 48px | Section hero headings |
| `text-display-md` | 36px | Modal/dialog headings |
| `text-display-sm` | 30px | Card titles, section headings |
| `text-display-xs` | 24px` | Subsection headings |

**Text scale** — body and UI copy:

| Class | Size | Use |
|-------|------|-----|
| `text-xl` | 20px | Large body, lead paragraphs |
| `text-lg` | 18px | Body large, card descriptions |
| `text-md` | 16px | Default body text |
| `text-sm` | 14px | Labels, form helper text |
| `text-xs` | 12px | Captions, timestamps, badges |

### Font Weights

| Class | Value | Use |
|-------|-------|-----|
| `font-regular` | 400 | Body text, descriptions |
| `font-medium` | 500 | Labels, navigation items |
| `font-semibold` | 600 | Headings, button text, emphasis |
| `font-bold` | 700 | Strong headings, callouts |

### Letter Spacing

- Tighten display headings: `tracking-tight` or `tracking-tighter`
- Default body: no explicit tracking class needed (inherits normal)
- Uppercase labels/badges: `tracking-wide` or `tracking-wider`

### Typography Checklist

- [ ] Heading hierarchy correct (only one `text-display-2xl` per page)
- [ ] Body text uses `text-md font-regular` as baseline
- [ ] Form labels use `text-sm font-medium`
- [ ] Never set raw `font-size` or `font-family` inline — tokens only
- [ ] Line height: headings use `leading-tight`, body uses default (`leading-normal`)

---

## 3. Spacing & Layout

### Spacing Scale

Use Tailwind spacing utilities. Prefer 4px multiples (gap-1=4px, gap-2=8px, gap-4=16px, gap-6=24px, gap-8=32px).

**Common patterns:**

| Context | Token |
|---------|-------|
| Between form fields | `gap-4` (16px) |
| Between sections | `gap-6` or `gap-8` |
| Inside card header/footer | `gap-3` (12px) |
| Icon + text inline | `gap-2` (8px) |
| Button group gap | `gap-2` |

### Card Layout

`Card` and `Card.Content` default to standard padding. Use `padding="none"` only when content needs to own its own edge-to-edge spacing.

```tsx
// Correct — standard padded card
<Card>
  <Card.Header>
    <Card.Title>Title</Card.Title>
  </Card.Header>
  <Card.Content>
    {/* content here, no extra padding wrapper needed */}
  </Card.Content>
</Card>

// Correct — edge-to-edge body content
<Card padding="none">
  <Card.Content padding="none">
    {/* table, media, or custom layout owns its own spacing */}
  </Card.Content>
</Card>
```

### Page Layout Pattern

```tsx
<AppShell.Root gap={12}>
  <AppShell.Sidebar>
    <SidebarProvider>
      <AppSidebar>{/* nav items */}</AppSidebar>
    </SidebarProvider>
  </AppShell.Sidebar>
  <AppShell.Panel flex={1}>
    <AppShellCard>
      <AppShellCard.Header>
        <AppShellCard.Title>Page Title</AppShellCard.Title>
      </AppShellCard.Header>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* content */}
      </div>
    </AppShellCard>
  </AppShell.Panel>
</AppShell.Root>
```

### Grid Patterns

| Layout | Classes |
|--------|---------|
| Single column | `grid grid-cols-1 gap-4` |
| Two-column | `grid grid-cols-1 gap-4 md:grid-cols-2` |
| Three-column | `grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3` |
| Four-column metric cards | `grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4` |
| Sidebar + main | `flex gap-6` with `w-64 shrink-0` + `flex-1 min-w-0` |

Adjacent dashboard filters that can fit together should use a responsive row or grid, such as `grid grid-cols-1 gap-3 md:grid-cols-2`, and stack only on narrow viewports. Do not render two full-width filter selects in a vertical column on desktop.

Use `MetricCard` for KPI tiles and summary metrics. Do not compose metric cards from raw `Card`, nested cards, or bordered `div` blocks when the content is a label, value, change, target, or sparkline.

### Shadows & Elevation

Use `elevation-*` tokens, not raw `shadow-*` utilities:

| Token | Use |
|-------|-----|
| `elevation-0` | Flat, no shadow (default page content) |
| `elevation-1` | Subtle card lift |
| `elevation-2` | Popovers, dropdowns |
| `elevation-3` | Modals, dialogs |
| `elevation-4` | Overlays |
| `elevation-5` | Highest z-layer (toasts, tooltips on modals) |

### Spacing Checklist

- [ ] `Card` / `Card.Content` use default spacing for standard cards and `padding="none"` only for edge-to-edge content
- [ ] Section gaps use `gap-6` or `gap-8`, not margins
- [ ] Page content has `p-6` from layout wrapper, not individual components
- [ ] No inline `style={{ padding: '...' }}` — Tailwind only
- [ ] Elevation tokens for shadows, not raw `shadow-md` etc.

---

## 4. Responsive Design

### Breakpoints

| Breakpoint | px | Target |
|------------|-----|--------|
| default | 320+ | Mobile portrait |
| `sm:` | 640+ | Mobile landscape / large phones |
| `md:` | 768+ | Tablet |
| `lg:` | 1024+ | Desktop |
| `xl:` | 1280+ | Wide desktop |
| `2xl:` | 1440+ | Large monitors |

### Mobile-First Rules

Write base styles for mobile, layer up:

```tsx
// Correct — mobile-first
<div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">

// Wrong — desktop-first (breaks on mobile)
<div className="grid grid-cols-3 gap-4">
```

### AppShell Auto-Collapse

`AppShell` auto-collapses sidebar on mobile (below `lg:`). No manual breakpoint logic needed.

```tsx
// AppShell handles responsive sidebar — just use AppShell.Root + AppShell.Sidebar
<AppShell.Root>
  <AppShell.Sidebar>
    <SidebarProvider>
      <AppSidebar>{/* nav */}</AppSidebar>
    </SidebarProvider>
  </AppShell.Sidebar>
  <AppShell.Panel flex={1}>{children}</AppShell.Panel>
</AppShell.Root>
```

### Dialog → Sheet on Mobile

Use `Sheet` for mobile-friendly panels; `Dialog` for desktop confirmations. Adaptive behavior:

```tsx
const isMobile = useMediaQuery('(max-width: 767px)')

return isMobile
  ? <Sheet open={open} onOpenChange={setOpen}>{content}</Sheet>
  : <Dialog open={open} onOpenChange={setOpen}>{content}</Dialog>
```

Or use `Drawer` (built-in responsive) for bottom-sheet patterns.

### Touch Targets

- Min touch target: `min-h-11` (44px) for interactive elements on mobile
- Buttons default correct size at `size="md"` and above
- Custom clickable areas: add `p-2` or use `min-h-11 min-w-11 flex items-center justify-center`

### Responsive Checklist

- [ ] No hardcoded pixel widths without responsive override
- [ ] Grid columns collapse to single on mobile (`grid-cols-1`)
- [ ] Modals/dialogs reviewed on 375px viewport — consider Sheet for complex forms
- [ ] Touch targets at least 44px on interactive elements
- [ ] `AppShell` used for all app pages — never manually build sidebar toggle logic
- [ ] No horizontal scrolling on mobile (check `overflow-x-hidden` on body if needed)
- [ ] Text not overflowing containers — use `truncate` or `break-words` where needed

---

## 5. Component Hardening

### Native Control Rule For Generated Product UI

Do not use raw native controls in generated product UI:

| Do not emit | Use instead |
| --- | --- |
| `<button>` | `Button` |
| `<input>` | `Input`, `NumberInput`, `FileInput`, or a field-capable component |
| `<select>` | `Select`, `ComboboxMenu`, or `Autocomplete` |
| `<textarea>` | `Textarea` or `RichTextarea` |
| `<input type="checkbox">` | `Checkbox` or `CheckboxGroup` |
| `<input type="radio">` | `RadioGroup` |

Raw native controls are acceptable only inside low-level primitive implementation files, never in generated app/page examples.

### Error States

Use smart field props on form atoms — auto-wrap with `Field` and show inline errors:

```tsx
// Input, Textarea, Select, Checkbox, RadioGroup, Slider all support these
<Input
  label="Email"
  error={errors.email?.message}
  description="We'll never share your email"
  placeholder="name@company.com"
/>

<Select label="Role" error={errors.role?.message} placeholder="Choose role…">
  <SelectItem value="admin">Admin</SelectItem>
</Select>

<Checkbox label="Accept terms" error={errors.agreed?.message} />
```

For complex forms, use `Form` molecule — integrates with react-hook-form.

### Loading States

Match loading state to scope:

| Scope | Component |
|-------|-----------|
| Single element (text, image) | `<Skeleton className="h-4 w-32" />` |
| Inline action in progress | `<Button loading>Saving…</Button>` |
| Section/list loading | `<LoadingIndicator size="md" />` centered in container |

```tsx
// Skeleton placeholder while data loads
{isLoading ? (
  <div className="flex flex-col gap-3">
    <Skeleton className="h-5 w-48" />
    <Skeleton className="h-4 w-full" />
    <Skeleton className="h-4 w-3/4" />
  </div>
) : (
  <ActualContent />
)}
```

### Empty States

Every list, table, or data section must handle empty data:

```tsx
{items.length === 0 ? (
  <EmptyState
    title="No results found"
    description="Try adjusting your filters or search terms."
    primaryAction={{ label: 'Clear filters', onClick: clearFilters }}
  />
) : (
  <DataTable data={items} columns={columns} />
)}
```

### Overflow & Truncation

```tsx
// Single-line truncation
<p className="truncate max-w-xs">{longTitle}</p>

// Multi-line clamp
<p className="line-clamp-2">{description}</p>

// Scrollable container
<ScrollArea className="h-64">
  {longList}
</ScrollArea>

// Responsive table
<div className="overflow-x-auto">
  <Table>…</Table>
</div>
```

### Keyboard & Focus

- All interactive components use Radix primitives — keyboard nav built in
- Never remove focus outlines with `outline-none` unless replacing with custom `focus-visible:ring-*`
- Use `focusable` wrappers for custom interactive areas: `tabIndex={0}` + `onKeyDown` handler
- Arrow key nav for lists/menus: use `DropdownMenu`, `CommandMenu`, or `Tabs` — already handled

### Screen Readers

```tsx
// Icon-only buttons must have an accessible label
<Button iconOnly aria-label="Close dialog">
  <X className="size-4" />
</Button>

// Decorative icons — hide from screen readers
<CheckCircle className="size-4" aria-hidden="true" />

// Dynamic status announcements
<div role="status" aria-live="polite" className="sr-only">
  {statusMessage}
</div>

// Loading state
<Button loading aria-label="Saving changes, please wait">Save</Button>
```

### Disabled States

```tsx
// Always use disabled prop, not pointer-events-none
<Button disabled={!isValid}>Submit</Button>
<Input disabled={isSubmitting} />

// Fieldset for disabling groups
<fieldset disabled={isSubmitting}>
  <Input label="Name" />
  <Input label="Email" />
</fieldset>
```

### Destructive Actions

Always confirm before irreversible actions:

```tsx
<AlertDialog>
  <AlertDialog.Trigger render={<Button variant="destructive" />}>
    Delete account
  </AlertDialog.Trigger>
  <AlertDialog.Popup>
    <AlertDialog.Header>
      <AlertDialog.Title>Delete account?</AlertDialog.Title>
      <AlertDialog.Description>
        This action cannot be undone. All data will be permanently deleted.
      </AlertDialog.Description>
    </AlertDialog.Header>
    <AlertDialog.Footer>
      <AlertDialog.Cancel render={<Button appearance="outline" />}>Cancel</AlertDialog.Cancel>
      <AlertDialog.Action onClick={handleDelete} render={<Button variant="destructive" />}>
        Delete
      </AlertDialog.Action>
    </AlertDialog.Footer>
  </AlertDialog.Popup>
</AlertDialog>
```

### Hardening Checklist

- [ ] All form fields show inline error via `error` prop (not separate `<p>`)
- [ ] Every async action has loading state (`loading` button, Skeleton, or LoadingIndicator)
- [ ] Product lists and tables handle empty state with `EmptyState`; chat transcripts use `AIEmptyState`
- [ ] Long strings use `truncate` or `line-clamp-*` — no uncontrolled overflow
- [ ] Icon-only buttons have `aria-label`
- [ ] Decorative icons have `aria-hidden="true"`
- [ ] Destructive actions require `AlertDialog` confirmation
- [ ] No `disabled` via CSS only — use `disabled` prop
- [ ] Keyboard nav works without mouse (tab through, activate with Enter/Space)
- [ ] No `outline-none` without replacement `focus-visible:ring-*`

---

## 6. Polish (Final Pass)

### Border Radius Consistency

| Context | Class |
|---------|-------|
| Cards, panels, modals | `rounded-lg` |
| Inputs, buttons, selects | `rounded-md` |
| Avatars, color swatches | `rounded-full` |
| Badges, pills | `rounded-full` |
| Tooltips, small chips | `rounded-sm` |

Never mix radii within same component — pick level for component type, use consistently on all children.

### Focus Rings

All interactive elements must show visible focus rings for keyboard users:

```tsx
// Standard focus ring (matches design system)
className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"

// On dark surfaces
className="focus-visible:ring-offset-background"
```

Built-in components (Button, Input, etc.) already include correct focus rings — only add manually for custom interactive elements.

### Transitions & Animations

Use shared motion utilities for all transitions:

```tsx
// Correct — shared motion utilities
className="transition-colors duration-150 ease-smooth"       // hover state changes
className="transition-[color,background-color,border-color,box-shadow,opacity,transform] duration-200 ease-smooth" // most UI transitions
className="transition-opacity duration-300 ease-decelerate"  // overlays, page transitions
```

**Easing by intent:**

| Token | Value | Use |
|-------|-------|-----|
| `ease-smooth` | balanced | Toggle states, color changes |
| `ease-decelerate` | decelerating | Overlays, menus, entered content |

### Reduced Motion

Always respect `prefers-reduced-motion`:

```tsx
// On custom animated elements
className="transition-[color,background-color,border-color,box-shadow,opacity,transform] duration-200 ease-smooth motion-reduce:transition-none motion-reduce:animate-none"
```

Built-in Radix/overlay components already respect this via `data-state` + CSS. For custom animations, check and apply `motion-reduce:` variants.

### Icon Sizing

| Context | Class | px |
|---------|-------|----|
| Inline text icon | `size-4` | 16px |
| Button icon, form addon | `size-5` | 20px |
| Avatar fallback icon | `size-6` | 24px |
| Empty state / hero icon | `size-8` to `size-12` | 32–48px |
| FeaturedIcon component | use `size` prop | auto |

Always use `size-*` (sets both width and height) — never set `w-` and `h-` separately for square icons.

### Toast Notifications (Sonner)

Use `Sonner` for all feedback toasts — never inline alerts for transient messages:

```tsx
import { toast } from 'sonner'

// Success
toast.success('Changes saved')

// Error
toast.error('Failed to save', { description: error.message })

// Loading → resolved
const id = toast.loading('Saving…')
// later:
toast.success('Saved!', { id })

// Promise shorthand
toast.promise(saveData(), {
  loading: 'Saving…',
  success: 'Saved!',
  error: 'Failed to save',
})
```

Place `<Sonner />` once at app root inside `ThemeProvider`.

### `cn()` Utility

Always use `cn()` for conditional/merged class names — never string concatenation:

```tsx
import { cn } from '@humain/ui'

// Correct
<div className={cn('base-class', isActive && 'active-class', className)}>

// Wrong — breaks Tailwind merge
<div className={`base-class ${isActive ? 'active-class' : ''} ${className}`}>
```

### Polish Checklist

- [ ] All cards use `rounded-lg`, inputs/buttons use `rounded-md`, avatars use `rounded-full`
- [ ] Radius consistent within each component (no mixed `rounded-lg`/`rounded-sm` siblings)
- [ ] Custom interactive elements have `focus-visible:ring-2 focus-visible:ring-ring`
- [ ] Hover/color transitions use `duration-150`
- [ ] Overlay/enter/exit transitions use `duration-200` or `duration-300`
- [ ] Easing matches intent (`ease-smooth` for simple state changes, `ease-decelerate` for entered content)
- [ ] Custom animations include `motion-reduce:` override
- [ ] Icons use `size-4` inline, `size-5` for buttons, `size-6`+ for display
- [ ] Icon-only decorative icons have `aria-hidden="true"`
- [ ] All transient feedback uses `toast.*` via Sonner — no inline status banners for momentary state
- [ ] All conditional class names use `cn()`, never template literals
- [ ] No hardcoded color values anywhere — all colors via semantic tokens
