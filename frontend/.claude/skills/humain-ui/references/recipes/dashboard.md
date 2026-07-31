# Dashboard Recipe

**Use:** AppShell, AppSidebar, AppShellCard, MetricCard, DataTable, BarChart/LineChart/DonutChart

Start with the page shell before writing chart/table JSX. Dashboard content belongs inside `AppShell.Panel`. Full dashboard pages default to a single `AppShellCard` dashboard shell: put the dashboard title/subtitle in `AppShellCard.Header`, then keep search, dashboard actions, tabs, metric cards, chart widgets, and tables inside that same card body. AppShellCard body padding defaults to standard spacing; pass `bodyPadding="none"` when the shell includes edge-to-edge tables or charts and add spacing to non-edge sections. Use `MetricCard` for KPI tiles and summary metrics instead of composing raw cards. Keep adjacent dashboard filters in a responsive row or grid when they can fit together.

```tsx
import {
  AppShell,
  AppShellCard,
  AppSidebar,
  Badge,
  Button,
  DataTable,
  Input,
  MetricCard,
  SidebarProvider,
  Tabs,
  type ColumnDef
} from '@humain/ui'
import { Activity, Filter, LayoutDashboard, Search, Settings, Share2, Users } from 'lucide-react'

// Sample data for charts
const revenueData = [
  { id: 'jan', label: 'Jan', values: { revenue: 38000, target: 35000 } },
  { id: 'feb', label: 'Feb', values: { revenue: 42000, target: 40000 } },
  { id: 'mar', label: 'Mar', values: { revenue: 40000, target: 42000 } },
  { id: 'apr', label: 'Apr', values: { revenue: 45000, target: 44000 } },
  { id: 'may', label: 'May', values: { revenue: 48000, target: 46000 } },
  { id: 'jun', label: 'Jun', values: { revenue: 52000, target: 50000 } },
]

// Table data and columns
interface Order {
  id: string
  customer: string
  amount: number
  status: 'completed' | 'pending' | 'cancelled'
}

const orders: Order[] = [
  { id: '1', customer: 'Acme Corp', amount: 1250, status: 'completed' },
  { id: '2', customer: 'Globex Inc', amount: 890, status: 'pending' },
  { id: '3', customer: 'Initech', amount: 2100, status: 'completed' },
]

const columns: ColumnDef<Order, unknown>[] = [
  { accessorKey: 'customer', header: 'Customer' },
  {
    accessorKey: 'amount',
    header: 'Amount',
    cell: ({ row }) => `$${row.original.amount.toLocaleString()}`,
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => (
      <Badge variant="dot" color={row.original.status === 'completed' ? 'success' : 'secondary'} size="sm">
        {row.original.status}
      </Badge>
    ),
  },
]

function Dashboard() {
  return (
    <AppShell.Root gap={12} className="h-dvh">
      <AppShell.Sidebar>
        <SidebarProvider connected>
          <AppSidebar logo={<span className="font-semibold">Operations</span>} collapsible="icon">
            <AppSidebar.Nav>
              <AppSidebar.NavItem icon={<LayoutDashboard />} label="Dashboard" href="/dashboard" isActive />
              <AppSidebar.NavItem icon={<Users />} label="Accounts" href="/accounts" />
              <AppSidebar.NavItem icon={<Settings />} label="Settings" href="/settings" />
            </AppSidebar.Nav>
          </AppSidebar>
        </SidebarProvider>
      </AppShell.Sidebar>

      <AppShell.Panel flex={1}>
        <AppShellCard bodyPadding="none">
          <AppShellCard.Header>
            <AppShellCard.Title>Revenue operations</AppShellCard.Title>
            <AppShellCard.Subtitle>March 2026 - Monthly performance</AppShellCard.Subtitle>
          </AppShellCard.Header>

          <div className="border-b border-border-subtle px-6 py-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <Input
                className="max-w-sm"
                placeholder="Type to search..."
                startIcon={<Search className="size-4" />}
              />
              <div className="flex items-center gap-2">
                <Button appearance="ghost" variant="secondary" size="icon-sm" aria-label="Filter dashboard">
                  <Filter className="size-4" />
                </Button>
                <Button appearance="ghost" variant="secondary" size="icon-sm" aria-label="Chart view">
                  <Activity className="size-4" />
                </Button>
                <Button appearance="ghost" variant="secondary" size="icon-sm" aria-label="Share dashboard">
                  <Share2 className="size-4" />
                </Button>
              </div>
            </div>

            <Tabs defaultValue="home" className="mt-4">
              <Tabs.List variant="pill">
                <Tabs.Trigger value="home">Home</Tabs.Trigger>
                <Tabs.Trigger value="accounts">Accounts</Tabs.Trigger>
                <Tabs.Trigger value="notifications">Notifications</Tabs.Trigger>
              </Tabs.List>
            </Tabs>
          </div>

          <div className="grid grid-cols-1 gap-4 px-6 py-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              title="Revenue"
              value={52000}
              valueFormatter={(n) => `$${(n / 1000).toFixed(0)}k`}
              change={18.5}
              changeSentiment="positive"
              description="vs last month"
              data={revenueData}
              series={[{ id: 'revenue', label: 'Revenue' }]}
              chartType="area"
            />
            <MetricCard
              title="Active Users"
              value={1284}
              change={12}
              changeSentiment="positive"
              description="vs last month"
            />
            <MetricCard
              title="Conversion Rate"
              value={0.032}
              valueFormatter={(n) => `${(n * 100).toFixed(1)}%`}
              changeOverride={-2.1}
              changeSentiment="negative"
              description="vs last month"
            />
            <MetricCard
              title="Open Orders"
              value={orders.length}
              change={4}
              changeSentiment="neutral"
              description="current queue"
            />
          </div>

          <div className="grid grid-cols-1 gap-4 px-6 pb-4 xl:grid-cols-2">
            <MetricCard
              title="Top services by sales"
              value={89}
              valueFormatter={(n) => `${n}%`}
              change={9}
              changeSentiment="positive"
              description="UI design"
            />
            <MetricCard
              title="Conversion rate"
              value={0.928}
              valueFormatter={(n) => `${(n * 100).toFixed(1)}%`}
              change={6.3}
              changeSentiment="positive"
              description="Compared to last month"
              data={revenueData}
              series={[{ id: 'revenue', label: 'Revenue' }]}
              chartType="area"
            />
          </div>

          <div className="border-t border-border-subtle">
            <DataTable
              columns={columns}
              data={orders}
              getRowId={(row) => row.id}
              enableSorting
              enablePagination
              pageSize={10}
            />
          </div>
        </AppShellCard>
      </AppShell.Panel>
    </AppShell.Root>
  )
}
```

## Agent Output Failure Checks

Before returning a generated dashboard, scan your JSX for these issues:

- `AppShellCard` without `AppShellCard.Header` and `AppShellCard.Title`.
- `AppShellCard.Title` text repeated as a body heading.
- Subtitle/context copy rendered as the first body paragraph instead of `AppShellCard.Subtitle`.
- Dashboard title, search, dashboard actions, tabs, metric cards, and widgets split across separate top-level `AppShellCard` sections instead of one single `AppShellCard` dashboard shell (`DASHBOARD_SHELL_001`).
- `DataTable` or chart body inside a default padded `AppShellCard`.
- KPI tiles or summary metrics built from raw `Card` or bordered `div` instead of `MetricCard`.
- Adjacent dashboard filters stacked in a vertical column when a responsive row or grid would fit.
- Back, Export, alert, or notification controls rendered in the card body instead of header-owned toolbar structure.
- Edge-to-edge table/chart utility actions rendered in right-side `AppShellCard.Actions` instead of a compact action row under the title.
- Bare app-page `DataTable`, or a flush table `AppShellCard`, rendered directly in `AppShell.Panel` instead of `<AppShellCard inset bodyPadding="none">` (`TABLE_CONTAINER_001`).
- Table search/filter controls split across separate full-width blocks instead of one padded responsive toolbar above the table (`TABLE_CONTROLS_001`).
- Raw `ChartContainer` config without `var(--chart-*)` or semantic token colors.
- Raw native controls such as `<button>`, `<input>`, `<select>`, or `<textarea>`.

For edge-to-edge data panels, use this shape:

```tsx
<AppShellCard bodyPadding="none">
  <AppShellCard.Header>
    <AppShellCard.Title>Revenue trend</AppShellCard.Title>
    <AppShellCard.Subtitle>Monthly performance against target</AppShellCard.Subtitle>
    <div className="mt-3 flex flex-wrap items-center gap-2">
      <Button appearance="outline" variant="secondary" size="sm">Export</Button>
      <Button appearance="ghost" variant="secondary" size="icon-sm" aria-label="Refresh">...</Button>
    </div>
  </AppShellCard.Header>
  <BarChart
    data={revenueData}
    series={[
      { id: 'revenue', label: 'Revenue', color: 'var(--chart-1)' },
      { id: 'target', label: 'Target', color: 'var(--chart-2)' },
    ]}
  />
</AppShellCard>
```

**Key props:**
- `AppShell.Root`: background (default: var(--app-background)), height, padding, mobilePadding, gap, connected, activePanel, onActivePanelChange, resizablePanels (default: true for eligible two-panel desktop layouts), defaultPanelSizes, panelSizes, onPanelSizesChange, expandedPanel, defaultExpandedPanel, onExpandedPanelChange, expandThreshold
- `AppShell.Panel`: width (fixed px), flex (flex-grow), minWidth, expanded, label (mobile tab), onExpandedChange
- `AppShellCard`: bodyPadding, bodyClassName, elevation, inset, Header, Title, Subtitle, Actions, Menu
- `MetricCard`: value (required), title, change, changeSentiment (positive|negative|neutral), data, series, chartType (line|bar|area), valueFormatter, size (sm|md|lg)
- `BarChart`: data, series, barMode (stacked|grouped), size (sm|default|lg|xl), showYAxis, showXAxis, yAxisFormat, legendPosition (none|top|right), barRadius
- `DataTable`: columns, data, getRowId (recommended), enableSorting, enablePagination, pageSize, paginationType, paginationShape, paginationSize (xs|sm|md|lg), enableRowSelection, responsiveColumns with column.meta.responsive, dividers (line|alternating), density (default|compact)
- `DataTable` responsive columns: opt in with responsiveColumns and set column.meta.responsive = { priority?: 'always'|'desktop'|'mobile', hideBelow?: 'sm'|'md'|'lg' }. Omitted priority/hideBelow defaults to desktop columns hidden below md; priorities 'always' and 'mobile' ignore hideBelow; Web Components use the same object as columns[].responsive.
- `DonutChart`: data (array of {value, maxValue?}), series, centerValue, centerLabel, size (xs|sm|md|lg), legendPosition (none|bottom|right)

**Required evidence before promoting a dashboard:** loading, empty, error, dense data, mobile, and dark-mode states have stories or screenshots. Avoid nested cards and double padding.

**Default background:** Keep the default `AppShell.Root` background for dashboards. It already uses `var(--app-background)` / `bg-app`; only pass `background` when intentionally replacing the app gradient with a solid or custom canvas.
