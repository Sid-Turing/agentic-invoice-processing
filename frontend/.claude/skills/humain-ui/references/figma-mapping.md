# Figma-to-Code Pipeline

Activated only when Figma URL provided (e.g., `https://figma.com/design/...?node-id=1-2`).

## Prerequisites

- Figma MCP server available (get_design_context, get_screenshot, get_metadata)
- Playwright MCP optional (screenshot verification)

## Pipeline

1. Extract node ID from URL (e.g., `?node-id=1-2` → `1:2`)
2. Get Figma screenshot via `get_screenshot` — visual reference
3. Get design context via `get_design_context` — structure, styles, layout
4. Map Figma elements to Humain components using table below
5. Generate React code with correct components, props, variants
6. Ask user: "Want screenshot to verify?" If yes, render via Playwright and screenshot

## Component Mapping

| Figma pattern | Humain component |
|---|---|
| Clickable frame with text + icon | `Button` (match variant by visual style) |
| Text field with label + helper text | `Input` (with `label`, `description` props) |
| Checkbox + label text | `Checkbox` (with `label` prop) |
| Toggle/switch control | `Switch` |
| Dropdown/select trigger | `Select` |
| Card frame with sections | `Card` + `Card.Header` + `Card.Content` + `Card.Footer` |
| Modal overlay with backdrop | `Dialog` |
| Destructive confirmation modal | `AlertDialog` |
| Side panel from edge | `Sheet` or `Drawer` |
| Table with rows/columns/headers | `DataTable` |
| Chart visualization | `BarChart` / `LineChart` / `DonutChart` |
| Chat bubble with avatar | `AIMessage` |
| Chat input bar | `AIInput` |
| Sidebar with nav items + logo | `AppSidebar` |
| Page with sidebar + content | `AppShell.Root` + `AppShell.Sidebar` + `AppShell.Panel` |
| Tab bar with indicators | `Tabs` |
| Status pill/tag | `Badge` |
| User photo circle | `Avatar` |
| Tooltip on hover | `Tooltip` |
| Breadcrumb trail | `Breadcrumb` |
| Progress bar | `Progress` (`circular` for radial progress) |

## Color Matching

1. Match closest Humain token first:
   - Primary: `--primary` (#009688) with `air-50` → `air-950`
   - Grays: `gray-50` → `gray-950`, plus `slate-50` → `slate-950`
   - Error: semantic `destructive` or primitive `red-50` → `red-950`
   - Warning: semantic `warning` or primitive `amber-50` → `amber-950`
   - Success: semantic `success` or primitive `green-50` → `green-950`
2. No close match → stop and call out the missing token. Use the closest semantic surface/text/status token for implementation and record the Figma hex as a note for design-system follow-up.

## Unmapped Elements

Figma elements with no matching Humain component:
- Build with plain JSX + Tailwind classes
- Use Humain semantic tokens for colors (`text-foreground`, `bg-app`, `bg-card`, `bg-background`)
- Use `bg-app` for the full app/page canvas. `AppShell.Root` applies it by default, so do not translate a Figma app background to wrapper `bg-background` unless the design intentionally shows a flat solid surface.
- Use closest Humain token colors. Do not emit raw hex, raw Tailwind palette colors, or `dark:` overrides in production code.
