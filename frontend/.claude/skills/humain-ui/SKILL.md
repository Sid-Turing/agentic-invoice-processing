---
name: humain-ui
description: Use when building, migrating, auditing, or bootstrapping React UI with @humain/ui, including pages, dashboards, app shells, forms, dialogs, data tables, charts, AI chat workspaces, or Figma-to-Humain mapping.
---

# Humain Foundation UI (v2.2.2)

Build product UI with `@humain/ui`, a React 18/19 component library with Tailwind v4, dark mode, design tokens, Web Component projections, and AI-facing references.

Core rule: use the library primitives, tokens, and documented composition patterns. Do not reinvent components, fork tokens, hand-write styles the system owns, or invent APIs absent from source, docs, examples, or generated references. If the library does not have what the task needs, say so and wrap a third-party tool at the boundary.

For architecture, source-of-truth precedence, and downstream-surface rules, follow the package architecture guidance available to your project. This skill is consumer UI guidance, not a replacement architecture contract.

## Quick Start

```tsx
npm install @humain/ui lucide-react
import '@humain/ui/styles.css'
import { ThemeProvider, Button, Input, Dialog } from '@humain/ui'

<ThemeProvider><App /></ThemeProvider>
```

For SSR, add `<ThemeScript />` in `<head>`. If `defaultTheme` or `storageKey` is customized, pass the same values to `ThemeScript` and `ThemeProvider`.

## Pre-Flight Gate

Run before any Build or Adopt task. Stop and fix the first failure.

| Check | How | If missing |
|-------|-----|------------|
| Package installed | `package.json` has `@humain/ui` | `npm install @humain/ui lucide-react` |
| Styles imported | `@humain/ui/styles.css` once at app root | Add it before writing UI |
| ThemeProvider wraps app | `<ThemeProvider>` ancestor of Humain components | Wrap the app |
| Tailwind v4 setup | Humain preset or `@theme` CSS binding | Use [bootstrap.md](references/bootstrap.md) |
| SSR flash guard | `<ThemeScript />` in SSR `<head>` | Add it with matching theme props |
| React 18/19 | `react` and `react-dom` 18+ | Upgrade first |

Adopting an existing project? Run the scan in [adoption.md](references/adoption.md) before this gate.

## Mode Detection

Always load [humain-identity.md](references/humain-identity.md) first.

| Signal | Mode | Required references |
|--------|------|---------------------|
| Build, create, add UI/component/page/feature | Build | [quality.md](references/quality.md) + task refs below |
| Migrate, adopt, convert, fix existing UI | Adopt | [adoption.md](references/adoption.md) + [foundations.md](references/foundations.md) |
| Set up, scaffold, bootstrap new project | Bootstrap | [bootstrap.md](references/bootstrap.md) + [foundations.md](references/foundations.md) + [templates.md](references/templates.md) |
| Figma URL provided | Build | [figma-mapping.md](references/figma-mapping.md) + task refs |

## Page Shape

Pick the page shape before writing JSX. If unclear, use **AppShell + single panel** or show two candidate shapes and ask.

| Shape | When | Skeleton |
|-------|------|----------|
| Standalone page | Auth, marketing, onboarding, error pages | `<PageBackground />` plus unframed page content |
| AppShell + single panel | Dashboard, list, settings, detail page | `<AppShell.Root><AppShell.Sidebar/><AppShell.Panel><AppShellCard>...` |
| AppShell + multi-panel | Master/detail, list plus detail, main content plus history/activity/supporting compartment, two-column tools | Sibling `AppShell.Panel` children; each titled work or supporting compartment uses `AppShellCard` |
| Chat + content | AI assistant beside generated output | `AppShell.Root` with left `AIContainer` panel and right `AppShellCard` panel |
| Modal flow | Confirm, edit-in-place, transient task | `Dialog`, `AlertDialog`, or mobile `Sheet` |

Default background rule: `AppShell.Root` owns the normal app canvas. Do not pass `background="var(--background)"`, `background="var(--surface-*)"`, or wrap with `bg-background` unless the user explicitly wants a flat surface.

## Reference Routing

Load only what the task needs.

| Building... | Load |
|-------------|------|
| Any UI | [foundations.md](references/foundations.md) |
| Buttons, inputs, badges | [atoms.md](references/atoms.md) |
| Forms with labels/errors | [atoms.md](references/atoms.md) + [molecules.md](references/molecules.md) + [forms recipe](references/recipes/forms.md) |
| Tabs, accordion, charts | [molecules.md](references/molecules.md) |
| Dialogs, menus, tooltips | [organisms.md](references/organisms.md) + [dialogs recipe](references/recipes/dialogs-and-overlays.md) |
| Data tables | [organisms.md](references/organisms.md) + [data-table recipe](references/recipes/data-table.md) |
| AI chat interface | [organisms.md](references/organisms.md) + [chat recipe](references/recipes/chat.md) |
| Dashboard with metrics | [molecules.md](references/molecules.md) + [organisms.md](references/organisms.md) + [dashboard recipe](references/recipes/dashboard.md) |
| Standard/golden path UI | [golden paths recipe](references/recipes/golden-paths.md) + component refs |
| App shell / sidebar / page layout | [templates.md](references/templates.md) |
| Auth pages | [pages recipe](references/recipes/pages.md) |
| Footgun or repeated failure | [incidents.md](references/incidents.md) |

Reverse routing:

| Reaching for... | Stop and load |
|-----------------|---------------|
| Hand-rolled sidebar toggle | [templates.md](references/templates.md) |
| `dark:` modifiers or raw colors | [foundations.md](references/foundations.md) + [quality.md](references/quality.md) |
| Removing card padding with ad hoc classes | [Default Padding](#default-padding) |
| Wrapping `Input` in `Field` just for a label | [Smart Field Props](#smart-field-props) |
| Manually positioning icons inside inputs | [Smart Field Props](#smart-field-props) |
| Forcing `SelectPopup` to overlap its trigger | [Smart Select Props](#smart-select-props) |
| Building a confirm modal from plain `Dialog` | [organisms.md](references/organisms.md) for `AlertDialog` |
| Hand-rolling a profile/settings/sign-out nav menu | [templates.md](references/templates.md) for `NavAccountMenu` |

## Build Loop

For build tasks, use two passes unless the user says "just do it" or the change is a narrow edit to existing UI.

1. Skeleton pass: page shape, `AppShell` panels, `AppShellCard` slots, component names, and data placeholders. No styling tweaks or final copy.
2. Fill pass: wire data, copy, states, interactions, and the [quality.md](references/quality.md) polish checks.

For interactive design-review requests, show the skeleton and wait. For implementation requests, use it as an internal checkpoint and state the key assumptions in the final note.

## Generated Output Guardrails

Check generated JSX against these rules before final output:

- Every titled product panel uses `AppShellCard` with `AppShellCard.Header` and `AppShellCard.Title`.
- Put descriptive card context in `AppShellCard.Subtitle`.
- Do not repeat `AppShellCard.Title` text as a body heading, label, or `SectionHeader` inside the same card.
- Use `bodyPadding="none"` when a card body is primarily `DataTable`, `BarChart`, `LineChart`, `DonutChart`, `PieChart`, `RadarChart`, `ChartContainer`, or edge-to-edge media.
- Prefer `DataTable` built-in pagination with `enablePagination`. Center standalone `Pagination` in a same-width footer below the table.
- Wrap app-page `DataTable` views in `<AppShellCard inset bodyPadding="none">` so the page has spacing while the table stays edge-to-edge inside its card. Do not render a flush table card directly against the panel edge.
- Keep table search and filters in one padded responsive toolbar between `AppShellCard.Header` and `DataTable`; do not split search/selects into separate full-width body blocks or repeat the title/count in the body.
- Prefer the flat `Select` API for dropdown fields and filters. If advanced `SelectRoot`/`SelectPopup` composition is required, keep the popup anchored below/above the trigger; do not set `alignItemWithTrigger` to true or manually position the popup over the trigger.
- Use `MetricCard` for KPI tiles and summary metrics instead of raw `Card` or bordered `div` compositions.
- Keep adjacent dashboard filters in a responsive row or grid when they can fit together; stack them only on narrow viewports.
- For full dashboard pages, use one single `AppShellCard` dashboard shell: put the title/subtitle in `AppShellCard.Header`, then keep search, dashboard actions, tabs, metric cards, chart widgets, and table content inside that same card body. Do not split dashboard header/search/metrics/widgets into separate top-level `AppShellCard` sections in one `AppShell.Panel`.
- Data/content app pages with Quick Link navigation use one `AppShellCard` document shell. Put the title/subtitle in `AppShellCard.Header`, then keep the main content and the Quick Link rail inside the same `AppShellCard` body with an internal responsive grid and divider. Do not split Quick Link into a separate top-level `AppShellCard`, bare `aside`, or sibling card.
- Use `PageHeader` for page-level title/subtitle/action headers when the screen is not already inside an `AppShellCard` toolbar. Primary actions belong on the right of the header when space allows, not stacked under the title.
- Move Back or drill-down navigation into `AppShellCard.Header`. Move primary create actions such as Add, Create, New, or Invite into `AppShellCard.Actions`; never stack them under `AppShellCard.Title`. For edge-to-edge data panels, metric definition tables, and chart/table panels, put Export, Refresh, alert, and notification utilities inside `AppShellCard.Header` below the title/subtitle as a compact wrapped action row. Reserve `AppShellCard.Actions` for compact non-data panel toolbar commands and primary create actions, with overflow in `AppShellCard.Menu`.
- Show at most two visible buttons in page or card headers. Move additional commands into an ellipsis More actions menu (`AppShellCard.Menu`, `DropdownMenu`, or the built-in PageHeader overflow).
- Use `Input startIcon`/`endIcon`, `Textarea startIcon`/`endIcon`, or component icon props for field icons. Do not absolutely position lucide icons over fields or compensate with manual padding.
- New, create, add, invite, and edit forms are dialog flows by default when launched from a list or detail screen. Trigger `Dialog` from the header/list, put fields in `Dialog.Body`, and put Cancel/Submit in `Dialog.Footer`; do not route to a standalone page just to show the transient form.
- Keep standard `AppShell.Panel` cards on the default raised surface: omit `elevation` so `AppShellCard` uses `elevation="md"` with the token-backed `shadow-md` treatment. Use `elevation="none"` only for intentionally flush panels.
- For main content plus supporting compartments such as History, Activity, Audit, Comments, or Changes, use sibling `AppShell.Panel`s and wrap both the main surface and the supporting compartment in `AppShellCard`. Do not render History or Activity as a bare `aside`, `div`, or floating panel next to a main `AppShellCard`.
- Chat applications with generated dashboards, tables, charts, or detail output must look like a two-panel workspace: left conversation rail with `AIContainer` directly in `AppShell.Panel`, right generated-output panel with `AppShellCard`. Do not combine the chat transcript and generated output in one `AppShellCard` or single-column surface.
- Do not compute `bodyPadding` with a ternary in chat workspaces; render separate `AppShellCard` branches for table, chart, and detail views so table/chart branches use literal `bodyPadding="none"` and detail/form branches keep default padding.
- Use `NavAccountMenu` for the default profile/settings/language/theme/sign-out navigation card. Do not hand-roll a profile dropdown or account menu from raw `div`, `Card`, or `Button` blocks.
- Use HUMAIN controls: `Button`, `Input`, `Select`, `Textarea`, `Checkbox`, `Switch`, `RadioGroup`, `Slider`, `DropdownMenu`. Do not use raw native controls in product UI unless implementing a low-level primitive.
- Use HUMAIN chart wrappers when possible. If using `ChartContainer` or Recharts primitives directly, every labeled series needs token-backed color: `var(--chart-1)` through `var(--chart-5)` or documented semantic tokens.

Canonical card pattern:

```tsx
<AppShellCard inset bodyPadding="none">
  <AppShellCard.Header>
    <AppShellCard.Title>Recent orders</AppShellCard.Title>
    <AppShellCard.Subtitle>Sortable order activity</AppShellCard.Subtitle>
  </AppShellCard.Header>
  <div className="border-b border-border-subtle px-6 py-4">
    <div className="grid grid-cols-1 gap-3 md:grid-cols-[minmax(0,320px)_repeat(2,minmax(180px,1fr))]">
      <Input placeholder="Search orders..." startIcon={<Search className="size-4" />} />
      <Select placeholder="All statuses" />
      <Select placeholder="All owners" />
    </div>
  </div>
  <DataTable columns={columns} data={orders} getRowId={(row) => row.id} />
</AppShellCard>
```

Avoid body-heading duplication:

```tsx
<AppShellCard>
  <h2>Recent orders</h2>
  <p>Sortable order activity</p>
  <DataTable columns={columns} data={orders} />
</AppShellCard>
```

## Core Patterns

### Compound Components

Prefer dot notation: `Dialog.Header`, `Dialog.Title`, `Sheet.Body`, `DropdownMenu.Item`, `AIContainer.Messages`, `AppShell.Panel`, `AppShellCard.Title`. Do not invent flattened names when compound parts exist.

### AppShellCard

Use `AppShellCard` as the default wrapper for titled product content inside `AppShell.Panel`. Key parts: `AppShellCard.Header`, `AppShellCard.Title`, `AppShellCard.Subtitle`, `AppShellCard.Actions`, `AppShellCard.Menu`.

Rules:

- Always render `AppShellCard.Header` with at least `AppShellCard.Title`; otherwise the expand button can drift left.
- Do not wrap `DataTable` in `Card`, and do not put `DataTable` inside a padded `AppShellCard` body. For app-page table panels, use `<AppShellCard inset bodyPadding="none">`.
- Back or drill-down navigation belongs in `AppShellCard.Header`. Primary create actions such as Add, Create, New, or Invite belong in `AppShellCard.Actions`, not under `AppShellCard.Title`. Data-panel utilities such as Export, Refresh, alerts, and notifications should sit inside `AppShellCard.Header` below the title/subtitle in a compact `mt-3 flex flex-wrap items-center gap-2` row.
- Use `AppShellCard.Actions` for primary create actions and compact non-data panel toolbar commands; put max two visible buttons there and move overflow to `AppShellCard.Menu`.
- Use `text-secondary-foreground` for readable custom body copy, table cells, timestamps, captions, and instructional text. Reserve `text-muted-foreground` for icons, placeholders, and low-emphasis metadata.

### Dashboard Shell

Dashboard pages use a single `AppShellCard` dashboard shell by default. Put the dashboard title and period/context in `AppShellCard.Header`; put search, dashboard actions, tabs, metric cards, chart widgets, and table content inside that same card body. Use `bodyPadding="none"` when the shell includes edge-to-edge table content, and add padding only to the non-edge sections such as search, tabs, and metric grids.

### Data App Content

Data/content app pages with Quick Link navigation use a single `AppShellCard` document shell by default. Put the app or product title and supporting context in `AppShellCard.Header`, then put the long-form content and Quick Link rail inside the same `AppShellCard` body. Use an internal responsive grid: main content on the left, Quick Link on the right with `border-l border-border-subtle` on desktop, and stacked sections on mobile.

### Chat + Content

Use exactly two panels for the default resizable desktop layout: a left conversation rail with `AIContainer` directly in `AppShell.Panel`, and a right generated-output workspace with `AppShellCard`. This is the default shape for chat applications that produce dashboards, tables, charts, reports, or detail views. Do not put the transcript, input, and generated output into one card or one column. Use `minWidth={320}` for pixel minimums and `minWidth="45%"` for percentage sizing. Root APIs (`panelSizes`, `onPanelSizesChange`, `expandedPanel`, `onExpandedPanelChange`) own resizable layouts.

Key rule: chat commands update `activeView`; the content panel renders separate `AppShellCard` branches for table, chart, and detail views. Use literal `bodyPadding="none"` for table and chart views. Pass one stable `autoScrollKey` to `AIContainer.Messages` when transcript rows are children rather than root `messages`.

### Main + Supporting Panels

For app workspaces that pair a main content surface with a supporting History, Activity, Audit, Comments, or Changes compartment, use two sibling `AppShell.Panel`s. The main panel gets its own `AppShellCard`; the supporting panel also gets an `AppShellCard` with `AppShellCard.Header` and `AppShellCard.Title`. This keeps the side compartment aligned with the shell instead of looking like an unrelated floating `aside`.

### Default Profile Navigation

Use `NavAccountMenu` as the default profile nav/account menu. The standard card menu is `NavAccountMenu` with `type="card"`, `NavAccountMenuTrigger`, `NavAccountMenuContent`, `NavAccountMenuHeader`, sectioned `NavAccountMenuItem`s for Platform and Configuration, Settings, language, `NavAccountMenuThemeSwitch`, and a `NavAccountMenuFooter` sign-out `Button`.

### Default Padding

Card-like containers default to standard padding. Opt out through props, not `p-0`, negative margins, or responsive overrides.

| Component | Default | Edge-to-edge opt-out |
|-----------|---------|----------------------|
| `AppShellCard` body | `bodyPadding="md"` | `bodyPadding="none"` |
| `Card` root | `padding="md"` | `padding="none"` |
| `Card.Content` | `padding="md"` | `padding="none"` |
| `Dialog.Body`, `Sheet.Body`, `Drawer` body | built-in body padding | `className="p-0"` only for full-bleed content |

### Smart Field Props

Form atoms accept `label`, `error`, `description`, `tooltip`, `required`, and related field props directly. Use `<Input label="Email" error={errors.email} />`; reserve compound `Field` for multi-control custom layouts. For field icons, use `startIcon`/`endIcon` instead of absolutely-positioned sibling icons and manual padding.

### Smart Select Props

Use the flat `<Select>` API for normal dropdown fields and filters. Its popup is anchored below or above the trigger by default. Use advanced `SelectRoot`/`SelectPopup` only for custom triggers, and keep `alignItemWithTrigger={false}` so the menu does not overlap the closed field or surrounding text.

### Render Props And State

Use `render` for polymorphic elements: `<Button render={<a href="/home" />}>Home</Button>`. Use uncontrolled components by default; use controlled props such as `open`/`onOpenChange` when app state owns the interaction.

## Anti-Slop

| Avoid | Why | Exception |
|-------|-----|-----------|
| Raw hex, `bg-blue-500`, `text-[#123]` | Breaks semantic tokens and dark mode | Storybook palette demos |
| `dark:` modifiers | Tokens already encode modes | Third-party widget boundary |
| Purple gradients, glassmorphism, cyan glow | Conflicts with brand identity | Explicit brand-approved marketing surface |
| Card nested in card | Doubles padding/shadow and weakens hierarchy | Never; use spacing or `Separator` |
| `outline-none` without replacement | Breaks keyboard focus | Never |
| Inline padding styles | Sidesteps tokens | Truly dynamic runtime value |
| Manual font import | Duplicates token-preferred Inter loading | Isolated brand surface |
| Custom sidebar toggle logic | `AppShell` owns mobile collapse | Never |
| `<SidebarProvider defaultOpen>` or redundant defaults | AppSidebar should start collapsed | Omit `defaultOpen` |
| Hand-rolled label wrappers around form atoms | Smart Field Props handle labels | Multi-control composite field |

## Build Self-Check

Any "no" means fix before shipping.

- Tokens only? Grep diff for `#[0-9a-fA-F]{3,8}`, `dark:`, raw `shadow-`, `text-[`, `bg-[`.
- Compound dot notation? Use `Dialog.Header`, `AppShellCard.Title`, not invented flat parts.
- No double padding? Tables/charts use `bodyPadding="none"` or `padding="none"` where edge-to-edge content is required, and app-page table cards use `inset` or an outer padded panel wrapper.
- Table controls grouped? Search and filter controls sit in one responsive toolbar, not in stacked full-width blocks.
- Table pagination aligned? Use built-in `DataTable` pagination or a centered same-width footer.
- Dashboard composition native? Use `MetricCard`, responsive filter rows, and toolbar-owned navigation/actions.
- Squint test passes? Primary content and groups remain legible.
- Empty/loading/error states? Use `EmptyState`, `AIEmptyState`, `Skeleton`, `LoadingIndicator`, and field `error` props.
- TypeScript clean? Run the project typecheck when code changes.
- Resizable sizing correct? Numbers are pixels, strings are percentages.

For mass-building, declare token choices in `tokens-spec.md` or `CLAUDE.md`: default theme, palette, accent, radius, density, chart token order, and any project-specific additions.

## Exceptions

| Situation | Action |
|-----------|--------|
| Figma URL but Figma MCP unavailable | Stop; ask for auth, node ID, or screenshot. Do not guess from URL alone. |
| Component missing from library | Say so; compose from primitives or recommend a third-party wrapper boundary. |
| Deprecated component requested | Use it if required, but flag deprecation and replacement. |
| MUI/Chakra prop has no Humain equivalent | Map closest equivalent and note migration gap. Do not fork a primitive. |
| Existing project mixes hex and tokens | New code uses tokens; palette cleanup is a follow-up unless requested. |
| User says "skip the skeleton, just build it" | Skip skeleton and list assumptions in the reply. |
| Time pressure | Skip skeleton and squint check only; do not skip tokens or empty/loading/error states. |
| Conflicting Figma and brand context | Stop and ask which is authoritative. |
| Pre-flight fails in an app that worked before | Diagnose setup regression before continuing. |
| Component source edit without `.stories.tsx` changelog | Add changelog; component edit is incomplete without it. |
