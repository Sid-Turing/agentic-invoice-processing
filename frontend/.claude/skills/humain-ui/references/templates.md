# Templates

Page-level layout components.

See also: [recipes/pages.md](recipes/pages.md) for a full App Shell recipe with working code.

### AppShell
Full application layout container

Props: background (CSS value, default: var(--app-background)), height, padding, mobilePadding, gap, connected, activePanel, onActivePanelChange, resizablePanels (default: true for eligible two-panel desktop layouts; set false to opt out), defaultPanelSizes, panelSizes, onPanelSizesChange, expandedPanel, defaultExpandedPanel, onExpandedPanelChange, expandThreshold

Also exports: AppShell.Root, AppShell.Sidebar, AppShell.Panel, AppShell.Content, AppShell.Header, PanelExpansionContext, usePanelExpansion

Default background: AppShell.Root already uses `var(--app-background)` through the `bg-app` canvas in light and dark mode. For normal app/product screens, omit `background`; do not wrap AppShell in `bg-background` or pass `background="var(--background)"` unless intentionally replacing the app gradient with a flat solid surface.

```tsx
<AppShell.Root
  gap={12}
  defaultPanelSizes={[68, 32]}
>
  <AppShell.Sidebar>
    <SidebarProvider connected>
      <AppSidebar>{/* nav items */}</AppSidebar>
    </SidebarProvider>
  </AppShell.Sidebar>
  <AppShell.Panel minWidth="45%" label="Main content">
    <AppShellCard>
      <AppShellCard.Header>
        <AppShellCard.Title>Project details</AppShellCard.Title>
        <AppShellCard.Subtitle>Primary workspace content</AppShellCard.Subtitle>
      </AppShellCard.Header>
      {/* main content */}
    </AppShellCard>
  </AppShell.Panel>
  <AppShell.Panel minWidth={320} label="History">
    <AppShellCard>
      <AppShellCard.Header>
        <AppShellCard.Title>History</AppShellCard.Title>
        <AppShellCard.Subtitle>Recent activity and changes</AppShellCard.Subtitle>
      </AppShellCard.Header>
      {/* ActivityFeed, NotificationPanel, or history rows */}
    </AppShellCard>
  </AppShell.Panel>
</AppShell.Root>
```

**AppShell.Panel props:** width (fixed px), flex (flex-grow), minWidth (number = px, string = CSS/Resizable size such as "45%"), expanded, label (mobile tab), onExpandedChange
**Resizable panels:** v1 is React-only. Eligible two-panel desktop layouts resize by default. Use exactly two AppShell.Panel children, do not combine with connected, and let AppShell.Root own the ResizablePanelGroup/Handle. Set resizablePanels={false} for legacy fixed width/flex panel sizing. AppShell API accepts number tuples for defaultPanelSizes/panelSizes; internal Resizable percentage props must be strings.
**AppShellCard:** Recommended card wrapper for panels. Fills its panel by default with `elevation="md"`, auto-renders expand/collapse via PanelExpansionContext, and uses `elevation="none"` only for intentionally flush panels.
**Main + supporting panels:** For History, Activity, Audit, Comments, or Changes side compartments, use sibling AppShell.Panel children and wrap both the main surface and supporting compartment in AppShellCard. Do not render the supporting compartment as a bare aside/div next to a main AppShellCard.

### AppShellCard
Card wrapper for AppShell panels with toolbar (header, actions, menu, expand/collapse)

Compound card wrapper for AppShell panels. Renders AppShell.Content internally and fills its panel by default.

Sub-components: AppShellCard.Toolbar, AppShellCard.Header, AppShellCard.Title, AppShellCard.Subtitle, AppShellCard.Actions, AppShellCard.Menu

```tsx
<AppShell.Panel flex={1} expanded={expanded} onExpandedChange={setExpanded}>
  <AppShellCard>
    <AppShellCard.Toolbar className="px-3 py-2 sm:px-4 sm:py-3">
      <AppShellCard.Header>
        <AppShellCard.Title>Dashboard</AppShellCard.Title>
        <AppShellCard.Subtitle>Welcome back</AppShellCard.Subtitle>
      </AppShellCard.Header>
      <div className="flex shrink-0 items-center gap-2">
        <Button appearance="outline" variant="secondary" size="sm">Export</Button>
      </div>
      <AppShellCard.Actions>
        <Button>Review</Button>
      </AppShellCard.Actions>
    </AppShellCard.Toolbar>
    <AppShellCard.Menu>
      {/* Import DropdownMenu when using menu items inside AppShellCard.Menu */}
      <DropdownMenu.Item>Option 1</DropdownMenu.Item>
    </AppShellCard.Menu>
    {/* body content */}
  </AppShellCard>
</AppShell.Panel>
```

Props: bodyPadding (none|md), bodyClassName, elevation (none|2xs|xs|sm|md|lg|xl|2xl), inset

**Toolbar:** Optional composable toolbar wrapper. Accepts div props and className so consumers can change toolbar padding/gap or insert custom controls while keeping Header, Actions, Menu, and expansion controls wired.
**Header:** Left side of toolbar (flex-1). Contains Title/Subtitle or custom content.
**Actions:** Right-side toolbar commands for compact non-data panels. Rendered between header and menu.
**Menu:** Kebab dropdown menu items. Wrapped in DropdownMenu automatically.
**Body padding:** Defaults to bodyPadding="md" for standard padded content. Use bodyPadding="none" for edge-to-edge tables, charts, or media.

**Generated output contract:**

- Use `AppShellCard.Header` for every titled product panel.
- Use `AppShellCard.Title` once. Do not duplicate the card title in the body as `h2`, `h3`, `SectionHeader`, label text, or a table/chart caption.
- Use `AppShellCard.Subtitle` for short descriptive context. Do not put subtitle-style context as the first paragraph in the body.
- Use `bodyPadding="none"` when `DataTable`, chart components, `ChartContainer`, or edge-to-edge media are the primary body content.
- Use `DataTable` built-in pagination when possible. If standalone `Pagination` is composed under a table, wrap it in a same-width centered footer such as `className="flex justify-center"` so it aligns with the table.
- Back or drill-down navigation belongs in `AppShellCard.Header`. For edge-to-edge `DataTable` or chart panels, metric definition tables, and other dense data panels, put Export, Refresh, alert, and notification utilities inside `AppShellCard.Header` below the title/subtitle as a compact `mt-3 flex flex-wrap items-center gap-2` row. Use `AppShellCard.Actions` only for compact non-data panel toolbar commands, with overflow in `AppShellCard.Menu`.
- Header toolbars show at most two visible action buttons. Move additional commands into a More actions ellipsis menu such as `AppShellCard.Menu`, `DropdownMenu`, or built-in `PageHeader` overflow.
- App-page tables need `<AppShellCard inset bodyPadding="none">` so the page container has spacing while the table stays edge-to-edge inside its card. Do not render a flush table card directly against the panel edge.
- Table search and filters belong in one padded toolbar section between `AppShellCard.Header` and `DataTable`, using a responsive row/grid. Do not split search and selects into separate full-width body blocks or repeat the card title/count in the body.
- Keep standard padded body content only for forms, metric grids, prose, empty states, and mixed layouts that need internal spacing.

```tsx
// Correct: edge-to-edge table body
<AppShellCard inset bodyPadding="none">
  <AppShellCard.Header>
    <AppShellCard.Title>Recent orders</AppShellCard.Title>
    <AppShellCard.Subtitle>Sortable order activity</AppShellCard.Subtitle>
    <div className="mt-3 flex flex-wrap items-center gap-2">
      <Button appearance="outline" variant="secondary" size="sm">Export</Button>
      <Button appearance="ghost" variant="secondary" size="icon-sm" aria-label="Refresh">...</Button>
    </div>
  </AppShellCard.Header>
  <div className="border-b border-border-subtle px-6 py-4">
    <div className="grid grid-cols-1 gap-3 md:grid-cols-[minmax(0,320px)_repeat(2,minmax(180px,1fr))]">
      <Input placeholder="Search orders..." startIcon={<Search className="size-4" />} />
      <Select placeholder="All statuses" />
      <Select placeholder="All owners" />
    </div>
  </div>
  <DataTable columns={columns} data={orders} getRowId={(row) => row.id} enablePagination />
</AppShellCard>

// Incorrect: duplicate body heading, split subtitle, and double table padding
<AppShellCard>
  <h2>Recent orders</h2>
  <p>Sortable order activity</p>
  <DataTable columns={columns} data={orders} />
</AppShellCard>
```

**Elevation:** Defaults to elevation="md" for standard raised panels. Supports the full Figma shadow scale: 2xs, xs, sm, md, lg, xl, and 2xl. Use elevation="none" only when an intentionally flush panel is needed.
**Inset:** Use inset only when you intentionally want margin around the card inside the panel.
**Expand button:** Auto-rendered when inside AppShell.Panel with expanded/onExpandedChange props or root-owned AppShell expansion context.

### AppSidebar
Full-featured app sidebar with nav, chat list, account, collapsible modes

Props: collapsible (offcanvas|icon|none), side (left|right), rounded, sidebarBgColor, logoSubtext
Sub-components: AppSidebar.Nav, AppSidebar.NavItem, AppSidebar.NavSection, AppSidebar.NavSub, AppSidebar.ChatList, AppSidebar.ChatItem, AppSidebar.Account

```tsx
<SidebarProvider>
  <AppSidebar logoSubtext="Dashboard" rounded>
    <AppSidebar.Nav>
      <AppSidebar.NavItem icon={<Home />} label="Home" isActive />
      <AppSidebar.NavItem icon={<Users />} label="Users" badge={3} />
      <AppSidebar.NavSection label="Analytics" />
      <AppSidebar.NavItem icon={<BarChart3 />} label="Reports" />
    </AppSidebar.Nav>
    <AppSidebar.Account name="Tareq Amin" subtitle="Administrator" isOnline />
  </AppSidebar>
  <SidebarInset>{content}</SidebarInset>
</SidebarProvider>
```

**NavItem props:** icon, label, isActive, badge (string|number), href, onClick, children (NavSub items)
**NavSub props:** label, isActive, badge, href, onClick
**NavSection props:** label (text when expanded, divider when collapsed)
**Account props:** name, subtitle, avatarSrc, isOnline, onExpand

### SidebarProvider
Sidebar context provider

### SidebarInset
Main content area adjacent to sidebar

### Sidebar
Base sidebar component

### AuthPageLayout
Standalone authentication page layout with logo, form pane, responsive optional aside panel, and optional decorative background pattern

Props: logo, title, description, aside, showAside, showAsideOnMobile, formMaxWidthClassName, formClassName, asideClassName, backgroundPattern

Default auth pages use a plain background. Pass `backgroundPattern` only when a decorative page pattern is desired.

Configured aside objects render the standard notched aside card with HUMAIN badge, supporting copy, bottom-right avatar cluster, and configurable avatar overflow. Use `showAsideOnMobile` only when the aside context should stack above/below the form on small screens; otherwise aside content stays desktop-only.

```tsx
<AuthPageLayout
  title="Confirm workspace access"
  description="Use your enterprise credentials to continue."
  showAsideOnMobile
  aside={{
    title: 'Secure access for enterprise teams',
    cardTitle: 'Protected session',
    cardDescription: 'Use this panel for trust, security, or onboarding context.',
    avatarOverflowCount: 12,
  }}
>
  {/* form body */}
</AuthPageLayout>
```

### NavAccountMenu
Account dropdown menu

Compound component for account dropdown menus in sidebar footer.

Props: type (card|simple), open, onOpenChange, defaultOpen
Sub-components: NavAccountMenuTrigger, NavAccountMenuContent, NavAccountMenuHeader, NavAccountMenuSection, NavAccountMenuItem, NavAccountMenuAccount, NavAccountMenuSeparator, NavAccountMenuFooter, NavAccountMenuThemeSwitch

```tsx
<NavAccountMenu type="card">
  <NavAccountMenuTrigger
    avatar={<Avatar fallback="Tareq Amin" alt="Tareq Amin" size="sm" />}
    name="Tareq Amin"
    email="tareq@humain.ai"
  />
  <NavAccountMenuContent side="right" align="end">
    <NavAccountMenuHeader
      title="Profile"
      subtitle="Last login 22 May, 2026 11:30pm"
    />
    <NavAccountMenuSeparator />
    <NavAccountMenuSection>
      <NavAccountMenuItem icon={<SlidersHorizontal />}>
        Platform and Configuration
      </NavAccountMenuItem>
      <NavAccountMenuItem icon={<Settings />}>Settings</NavAccountMenuItem>
      <NavAccountMenuItem
        icon={<Globe />}
        render={(props) => (
          <button type="button" {...props}>
            <div className="flex flex-1 items-center justify-between">
              {props.children}
              <ChevronDown className="size-4 text-muted-foreground" />
            </div>
          </button>
        )}
      >
        English
      </NavAccountMenuItem>
    </NavAccountMenuSection>
    <NavAccountMenuSeparator />
    <NavAccountMenuSection>
      <NavAccountMenuThemeSwitch
        variant="theme-switch"
        size="sm"
        label="Light Mode"
      />
    </NavAccountMenuSection>
    <NavAccountMenuSeparator />
    <NavAccountMenuFooter>
      <Button variant="primary" shape="rounded" className="w-full gap-2">
        <LogOut className="size-4" />
        Sign Out
      </Button>
    </NavAccountMenuFooter>
  </NavAccountMenuContent>
</NavAccountMenu>
```

Use this profile card pattern for the default account navigation. Do not hand-roll a profile/settings/sign-out menu from raw divs, Card, or loose Button blocks.

**Trigger props:** avatar, name, email, badge, showLogoutButton, onLogout, compact
**Section props:** label, bordered (default false), children
**Item props:** icon, shortcut, destructive, disabled, onSelect, render (polymorphic)
**Account props:** avatar, name, email, selected, onSelect

### PageBackground
Decorative page background

Applies behind the main content area. Place it inside a relative container and keep page content above it.

```tsx
<div className="relative overflow-hidden">
  <PageBackground pattern="grid" offset="top" />
  <main className="relative z-10">...</main>
</div>
```

### ThemeProvider
Theme context provider with localStorage persistence, cross-tab sync, light/dark modes

Required for dark mode. Wrap entire app.

```tsx
import { ThemeProvider, ThemeScript } from '@humain/ui'

// SSR (Next.js, Remix)
<html suppressHydrationWarning>
  <head><ThemeScript /></head>
  <body><ThemeProvider>{children}</ThemeProvider></body>
</html>

// suppressHydrationWarning is required because ThemeScript mutates <html> before hydration
// If customizing SSR defaults, pass matching defaultTheme/storageKey to both:
// <ThemeScript defaultTheme="dark" storageKey="my-app-theme" />
// <ThemeProvider defaultTheme="dark" storageKey="my-app-theme">{children}</ThemeProvider>

// Vite SPA
<ThemeProvider><App /></ThemeProvider>
```

Theme hook: `const { theme, setTheme, toggleTheme } = useTheme()`
