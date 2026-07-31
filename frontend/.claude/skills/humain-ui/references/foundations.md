# Foundations

Design tokens, icons, animations, and composition patterns for `@humain/ui`.

## CSS & Design Tokens

### CSS Imports

| Export | Use |
|--------|-----|
| `styles.css` | Default -- includes Tailwind + components + tokens |
| `tokens.css` | Tokens only -- for apps with their own Tailwind |

### Semantic Color Tokens (auto-switch in dark mode)

Text: `text-foreground`, `text-secondary-foreground`, `text-muted-foreground`, `text-text-quaternary`

Use `text-secondary-foreground` for readable custom body copy, table cells, timestamps, captions, and instructional text you write directly. Component-provided `Description` and `Subtitle` parts may keep their built-in token defaults. Reserve direct `text-muted-foreground` utilities for icons, placeholders, and decorative metadata only.
Status: `text-destructive`, `text-warning`, `text-success`, `text-info`
Background: `bg-app`, `bg-background`, `bg-card`, `bg-surface-1`, `bg-surface-2`, `bg-muted`, `bg-primary`, `bg-destructive`
Border: `border-border`, `border-primary`, `border-destructive`

### Brand Colors

Primary: Humain aqua `bg-primary` (#009688). Air palette starts at `bg-air-50` and centers on `bg-air-500` (#00b89c).

**Secondary palettes** (all available as Tailwind utilities):
- `air-*`: Air (500: #00b89c)
- `oasis-*`: Oasis (500: #9acc1a)
- `slate-*`: Slate (500: #64748b)

**Decorative palettes** (50–900 range):
- `blue-*`: Blue (500: #3b82f6)
- `indigo-*`: Indigo (500: #6366f1)
- `orange-*`: Orange (500: #f97316)
- `pink-*`: Pink (500: #ec4899)
- `purple-*`: Purple (500: #a855f7)

**Primitive status palettes** (25–950 range, for backgrounds/borders beyond semantic tokens):
- `amber-*`: Amber / warning (500: #f59e0b)
- `gray-*`: Gray (500: #6b7280)
- `green-*`: Green / success (500: #22c55e)
- `red-*`: Red / destructive (500: #ef4444)

### Chart Colors

Categorical palette sourced from the Humain OS token JSON. The current order is aqua -> air teal -> oasis dark -> oasis accent -> oasis light. These tokens are brand-forward rather than rainbow hues, so use them in order and add semantic `series.color` overrides only when a chart needs stronger category separation.

| Token | Light | Use |
|-------|-------|-----|
| `chart-1` | `#009688` | Series 1 (primary aqua) |
| `chart-2` | `#2ecab1` | Series 2 (air teal) |
| `chart-3` | `#7fae14` | Series 3 (oasis dark) |
| `chart-4` | `#b8e636` | Series 4 (oasis accent) |
| `chart-5` | `#e1f88a` | Series 5 (oasis light) |
| `slate-500` | `#64748b` | Baseline / "other" series |

Override per-series via `series.color` (any CSS color). Prefer CSS variable values such as `var(--chart-1)` or `var(--success)` so overrides stay connected to the token system.

### Humain Brand Colors

- `humain-air`: `#00b89c`
- `humain-aqua`: `#009688`
- `humain-oasis`: `#b8e636`
- `humain-oasis-dark`: `#9acc1a`
- `humain-oasis-light`: `#d0f94a`
- `humain-stone`: `#f5f5f5`

### Surface & Background Hierarchy

Use the right background token for each context:

Default app/product screens use the app canvas automatically through `AppShell.Root` (`var(--app-background)` / `bg-app`). Do not add a wrapper `bg-background` or pass `background="var(--background)"` unless you intentionally want to remove the gradient.

| Token | Use Case | Light | Dark |
|-------|----------|-------|------|
| `bg-app` | Default app/product canvas | `var(--app-background)` | `var(--app-background)` |
| `bg-background` | Intentional solid surface | `#ffffff` | `#161616` |
| `bg-card` | Cards, modals, panels | `#ffffff` | `#ffffff08 (semi-transparent)` |
| `bg-popover` | Dropdowns, tooltips | `#fffffff2` | `#000000f2` |
| `bg-muted` | Subtle, disabled states | `#00000005` | `#ffffff05` |
| `bg-surface-1` | First elevation | `#fafafa` | `#07090c` |
| `bg-surface-2` | Second elevation | `#f5f5f5` | `#121212` |
| `bg-surface-3` | Third elevation | `#eeeeee` | `#1f1f1f` |
| `bg-accent` | Hover, selected | `#f5f5f5` | `#262626` |

**Key distinction:** `bg-app` is the default app/page canvas and carries the green gradient in light and dark mode; `bg-background` is a flat solid surface; `bg-card` is semi-transparent in dark mode and layers over the canvas.

**When to use which:**
- Default app/page background: `bg-app` (usually via `AppShell.Root`)
- Intentional solid standalone surface: `bg-background`
- Card/modal/sheet surface: `bg-card`
- Floating menus/tooltips: `bg-popover`
- Input backgrounds, skeletons: `bg-muted`
- Nested sections within cards: `bg-surface-1/2/3`
- Hover/selected states: `bg-accent`

### Motion Utilities

Use Tailwind duration utilities with the generated easing bindings: `duration-150`, `duration-200`, `duration-300`, `ease-smooth`, `ease-decelerate`, and `motion-reduce:*` variants.

## Icons

Icons come from `lucide-react` (peer dependency). Tree-shakeable -- only imported icons are bundled.

```tsx
import { Home, Search, ChevronDown } from 'lucide-react'
```

Sizing: `className="size-4"` (16px), `size-5` (20px), `size-6` (24px)

Component props: `startIcon`, `endIcon`, `icon`, `iconOnly`

```tsx
<Button startIcon={<Search className="size-5" />}>Search</Button>
<Input startIcon={<Search className="size-5" />} placeholder="Search..." />
<AppSidebar.NavItem icon={<Home />} label="Dashboard" />
<DropdownMenu.Item icon={<Settings />}>Settings</DropdownMenu.Item>
```

## Animations

Built on tw-animate-css. Overlays animate automatically.

| Class | Effect |
|-------|--------|
| `animate-in` / `animate-out` | Entry/exit container |
| `fade-in-0` / `fade-out-0` | Opacity 0->1 / 1->0 |
| `zoom-in-95` / `zoom-out-95` | Scale 95%->100% / 100%->95% |
| `slide-in-from-top-2` | Slide from top 8px |
| `slide-in-from-bottom-2` | Slide from bottom 8px |
| `animate-spin` | Continuous rotation |
| `animate-pulse` | Gentle opacity pulse |

Duration: `duration-100`, `duration-200`, `duration-300`
Reduced motion: `motion-reduce:animate-none`

Data attributes: `data-open:animate-in`, `data-closed:animate-out`

## Composition Patterns

**Compound components:** `Dialog` -> `Dialog.Trigger` + `Dialog.Popup` + `Dialog.Header` + `Dialog.Title` + `Dialog.Body` + `Dialog.Footer` + `Dialog.Action` + `Dialog.Cancel`

**Controlled:** `<Dialog open={open} onOpenChange={setOpen}>` -- you manage state
**Uncontrolled:** `<Dialog><Dialog.Trigger render={<Button />}>Open</Dialog.Trigger><Dialog.Popup>...</Dialog.Popup></Dialog>` -- component manages state

**Render props (polymorphic):**
```tsx
<Button render={<a href="/home" />}>Link styled as button</Button>
<Dialog.Close render={<Button appearance="outline" />}>Cancel</Dialog.Close>
```

**Smart field props:** Form atoms accept label/error/description directly. Zero overhead when unused.
Use component icon props (`startIcon`, `endIcon`, `icon`) for field icons. Do not manually absolutely-position lucide icons over inputs or textareas.
```tsx
<Input label="Email" error={errors.email} placeholder="name@co.com" />
<Select label="Role" placeholder="Choose...">{items}</Select>
<Checkbox label="I agree" error={errors.terms} />
```
