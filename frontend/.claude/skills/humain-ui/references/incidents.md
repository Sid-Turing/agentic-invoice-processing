# Incidents — Why Rules Exist

Dated lessons from real bugs. Each entry: what broke, why, rule that prevents recurrence. Append new entries at top.

Use this file when:
- Tempted to relax a rule that "looks redundant"
- Hitting a footgun the linter/types didn't catch
- Onboarding — read once to internalize the gotchas

---

## 2026-07-19 · Consumer Tailwind pass reordered packaged component utilities

**What broke**: New React 19 Vite and Next.js examples imported the compiled
HUMAIN stylesheet and then ran a second Tailwind v4 build. The pages built, but
responsive spacing drifted; in the Next.js example, the later base `gap-4`
rule overrode the package's earlier `sm:gap-6` rule at desktop widths.

**Cause**: The examples mixed the zero-config `styles.css` bootstrap path with
an app-owned Tailwind pipeline, and they were not registered in the repository's
example projection contract. Build and HTTP smoke checks passed without a
computed-style or contract-test assertion.

**Rule**: Zero-config examples import `@humain/ui/styles.css` once
and do not run another Tailwind pass. If an application owns its Tailwind
pipeline, follow the documented tokens-only integration as a separate path.
In-repository examples must also be registered in `EXAMPLE_PROJECTIONS` and
pass `tooling/ui/__tests__/example-imports.test.ts`.

**Detection**: Assert one packaged stylesheet import, reject a second Tailwind
import/plugin on the zero-config path, run the example contract test, and check
desktop/mobile computed spacing in a real browser.

## 2026-07-02 · Table page flush edge and split filters

**What broke**: Generated supplier list pages put a table card directly against the app panel edge, then placed duplicate title/count copy, search, and filters as separate stacked body blocks. The result looked cramped: the table had no page-level breathing room, the header contract was unclear, and controls did not scan as one toolbar.

**Cause**: The output conflated two different spacing rules. `DataTable` should be edge-to-edge inside its card via `bodyPadding="none"`, but a full app-page table card still needs panel spacing through `inset` or a padded panel wrapper. Search and filters also need one responsive toolbar rather than separate full-width fields.

**Rule**: For app-page table/list views, use `<AppShellCard inset bodyPadding="none">`. Put the title and count/context in `AppShellCard.Header` and `AppShellCard.Subtitle`. If search or filters exist, put them in one padded toolbar between the header and `DataTable`.

```tsx
<AppShell.Panel flex={1} label="Suppliers">
  <AppShellCard inset bodyPadding="none">
    <AppShellCard.Header>
      <AppShellCard.Title>Suppliers</AppShellCard.Title>
      <AppShellCard.Subtitle>8 suppliers</AppShellCard.Subtitle>
    </AppShellCard.Header>
    <div className="border-b border-border-subtle px-6 py-4">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-[minmax(0,320px)_repeat(2,minmax(180px,1fr))]">
        <Input placeholder="Search suppliers..." startIcon={<Search className="size-4" />} />
        <Select placeholder="All stages" />
        <Select placeholder="All risk levels" />
      </div>
    </div>
    <DataTable columns={columns} data={suppliers} getRowId={(row) => row.id} enablePagination />
  </AppShellCard>
</AppShell.Panel>
```

**Detection**: Harness rule `TABLE_CONTAINER_001` catches bare or flush app-page table panels. Harness rule `TABLE_CONTROLS_001` catches split table search/filter controls.

---

## 2026-07-01 · Primary card action stacked under title

**What broke**: Generated supplier-management panels placed the primary Add Supplier button inside the `AppShellCard.Header` title stack. The card header became a tall empty band with the CTA sitting under the title instead of in the right toolbar.

**Cause**: The output treated a primary page action like header body content. `AppShellCard.Header` owns the title, subtitle, back/drill-down controls, and compact data-panel utility rows. Primary create actions need the right-side toolbar slot.

**Rule**: Put primary Add, Create, New, and Invite actions in `AppShellCard.Actions`. Do not stack primary CTAs under `AppShellCard.Title` or render them as the first body element after the header.

**Detection**: Harness rule `ASC_HEADER_ACTIONS_001` catches primary create actions in the card body or header title stack.

---

## 2026-06-29 · Data app quick links split from content

**What broke**: A HUMAIN Nexus data platform app screenshot showed the desired shape as one `AppShellCard` document shell: title/subtitle in the card header, long-form data/product content in the main body, and Quick Link navigation as a right rail inside the same card. The risky generated shape is to put Quick Link in a separate top-level card or bare sidebar beside the content card.

**Cause**: The output treated local document navigation as a supporting app panel instead of part of the same data/content document surface.

**Rule**: Data/content app pages with Quick Link navigation use one `AppShellCard` shell. Keep the main content and Quick Link rail inside the same card body with an internal responsive grid and desktop divider.

```tsx
<AppShell.Panel flex={1} label="Data">
  <AppShellCard bodyPadding="none">
    <AppShellCard.Header>
      <AppShellCard.Title>HUMAIN Nexus</AppShellCard.Title>
      <AppShellCard.Subtitle>Built internally. Secured by design.</AppShellCard.Subtitle>
    </AppShellCard.Header>
    <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_220px]">
      <main className="space-y-6 px-6 py-5">
        <p>Enterprise-grade data platform content.</p>
      </main>
      <aside className="border-l border-border-subtle px-4 py-5">
        <p className="text-sm font-medium">Quick Link</p>
      </aside>
    </div>
  </AppShellCard>
</AppShell.Panel>
```

**Detection**: Harness rule `DATA_APP_QUICKLINK_001` catches AppShell data/content output that contains Quick Link navigation but does not keep it inside the same `AppShellCard` as the main content.

## 2026-06-29 · Dashboard shell scattered across cards

**What broke**: A monthly performance dashboard screenshot showed the desired shape as one large `AppShellCard` with title/subtitle, search, dashboard actions, tabs, metric cards, and analytics widgets inside the same workspace. The risky generated shape is to split the dashboard header, search/tabs, metrics, and widgets into separate top-level `AppShellCard`s inside one `AppShell.Panel`.

**Cause**: The output treated each dashboard region as a standalone panel instead of one dashboard workspace shell with internal sections.

**Rule**: Full dashboard pages use a single `AppShellCard` dashboard shell. Put title and context in `AppShellCard.Header`; keep search, dashboard actions, tabs, metric cards, chart widgets, and tables inside that same card body. Use `bodyPadding="none"` when edge-to-edge table content is present, and add padding only to non-edge sections.

```tsx
<AppShell.Panel flex={1} label="Dashboard">
  <AppShellCard bodyPadding="none">
    <AppShellCard.Header>
      <AppShellCard.Title>Humain Core</AppShellCard.Title>
      <AppShellCard.Subtitle>March 2026 - Monthly Performance</AppShellCard.Subtitle>
    </AppShellCard.Header>
    <div className="border-b border-border-subtle px-6 py-4">
      <Input placeholder="Type to search..." />
      <Tabs defaultValue="home">
        <Tabs.List>
          <Tabs.Trigger value="home">Home</Tabs.Trigger>
        </Tabs.List>
      </Tabs>
    </div>
    <div className="grid grid-cols-1 gap-4 px-6 py-4 md:grid-cols-3">
      <MetricCard title="Total Enroll" value={1500} />
      <MetricCard title="Total Course" value={2500} />
      <MetricCard title="Visitors" value={75000} />
    </div>
  </AppShellCard>
</AppShell.Panel>
```

**Detection**: Harness rule `DASHBOARD_SHELL_001` catches dashboard-labeled `AppShell.Panel` output that contains dashboard content but splits it across multiple top-level `AppShellCard`s.

## 2026-06-29 · Supporting history rendered as a bare side panel

**What broke**: A generated workspace paired a large main `AppShellCard` with a History compartment rendered as a separate bare `aside`/`div`. The History panel looked disconnected from the app shell, even though the desired pattern was a main `AppShellCard` plus a supporting `AppShellCard` side compartment.

**Cause**: The output treated History, Activity, Audit, Comments, and Changes as decorative sidebars instead of first-class `AppShell.Panel` content.

**Rule**: For main content plus supporting compartments, use sibling `AppShell.Panel`s. Wrap both the main workspace and the supporting compartment in `AppShellCard` with `AppShellCard.Header` and `AppShellCard.Title`.

```tsx
<AppShell.Root defaultPanelSizes={[68, 32]}>
  <AppShell.Panel minWidth="45%" label="Main content">
    <AppShellCard>
      <AppShellCard.Header>
        <AppShellCard.Title>Project details</AppShellCard.Title>
      </AppShellCard.Header>
      {/* main content */}
    </AppShellCard>
  </AppShell.Panel>
  <AppShell.Panel minWidth={320} label="History">
    <AppShellCard>
      <AppShellCard.Header>
        <AppShellCard.Title>History</AppShellCard.Title>
      </AppShellCard.Header>
      {/* history rows */}
    </AppShellCard>
  </AppShell.Panel>
</AppShell.Root>
```

**Detection**: Harness rule `SUPPORTING_PANEL_001` catches multi-panel `AppShell` output where a supporting History/Activity/Audit/Comments/Changes panel is rendered without `AppShellCard`.

## 2026-06-29 · Profile nav hand-rolled instead of NavAccountMenu

**What broke**: Generated profile navigation recreated the profile card manually with raw `div`s, loose buttons, and ad hoc rows for Profile, Last login, Platform and Configuration, Settings, language, theme, and Sign Out.

**Cause**: The output missed the template-level account menu component and rebuilt a standard nav pattern from primitives.

**Rule**: Use `NavAccountMenu type="card"` with `NavAccountMenuTrigger`, `NavAccountMenuContent`, `NavAccountMenuHeader`, sectioned `NavAccountMenuItem`s, `NavAccountMenuThemeSwitch`, and `NavAccountMenuFooter` for default profile/settings/language/theme/sign-out navigation.

```tsx
<NavAccountMenu type="card">
  <NavAccountMenuTrigger name="Tareq Amin" email="tareq@humain.ai" />
  <NavAccountMenuContent side="right" align="end">
    <NavAccountMenuHeader
      title="Profile"
      subtitle="Last login 22 May, 2026 11:30pm"
    />
    <NavAccountMenuSection>
      <NavAccountMenuItem>Platform and Configuration</NavAccountMenuItem>
      <NavAccountMenuItem>Settings</NavAccountMenuItem>
      <NavAccountMenuItem>English</NavAccountMenuItem>
    </NavAccountMenuSection>
    <NavAccountMenuSection>
      <NavAccountMenuThemeSwitch variant="theme-switch" label="Light Mode" />
    </NavAccountMenuSection>
    <NavAccountMenuFooter>
      <Button variant="primary" shape="rounded">Sign Out</Button>
    </NavAccountMenuFooter>
  </NavAccountMenuContent>
</NavAccountMenu>
```

**Detection**: Harness rule `NAV_ACCOUNT_MENU_001` catches profile/settings/sign-out menu output that contains the default account-menu text but does not use `NavAccountMenu`.

## 2026-06-29 · Chat output collapsed into one card

**What broke**: A chat application screenshot showed the desired pattern as a left conversation rail with user and assistant messages plus input, alongside a right generated loan application dashboard. The risky generated shape is to put the transcript, input, and dashboard/table output into one `AppShellCard` or one vertical column.

**Cause**: The output treated "chat application" as a single panel instead of an assistant workspace where chat commands produce a separate generated-output surface.

**Rule**: Chat applications that generate dashboards, tables, charts, or detail views use `AppShell.Root` with exactly two sibling `AppShell.Panel`s. Put `AIContainer` directly in the left chat panel. Put generated output in the right panel, usually inside `AppShellCard`, with separate table/chart/detail branches.

```tsx
<AppShell.Root defaultPanelSizes={[35, 65]}>
  <AppShell.Panel minWidth={320} label="Assistant">
    <AIContainer messages={messages}>
      <AIContainer.Messages />
      <AIContainer.Input inputProps={{ onSubmit: handleSend }} />
    </AIContainer>
  </AppShell.Panel>
  <AppShell.Panel minWidth="45%" label="Generated output">
    <AppShellCard bodyPadding="none">
      <AppShellCard.Header>
        <AppShellCard.Title>Loan Application Dashboard</AppShellCard.Title>
      </AppShellCard.Header>
      <DataTable columns={columns} data={rows} />
    </AppShellCard>
  </AppShell.Panel>
</AppShell.Root>
```

**Detection**: Harness rule `CHAT_LAYOUT_001` catches TSX output that contains chat UI plus generated data/chart/metric output without the sibling-panel workspace pattern.

## 2026-06-29 · Data-panel actions stretched across the header

**What broke**: A generated metric definitions table placed Export and Refresh controls in the right side of the `AppShellCard` toolbar, leaving the title isolated on the left and a wide empty header span between the title and actions.

**Cause**: The output followed the generic `AppShellCard.Actions` toolbar pattern for a dense table panel. That pattern works for compact non-data panel commands, but table/chart utilities read better as a short row directly under the title block.

**Rule**: For edge-to-edge `DataTable`, chart, metric definition, and other dense data panels, keep utility controls such as Export, Refresh, alerts, and notifications inside `AppShellCard.Header` below `AppShellCard.Title` / `AppShellCard.Subtitle`:

```tsx
<AppShellCard bodyPadding="none">
  <AppShellCard.Header>
    <AppShellCard.Title>Metric Definitions</AppShellCard.Title>
    <div className="mt-3 flex flex-wrap items-center gap-2">
      <Button appearance="outline" variant="secondary" size="sm">Export</Button>
      <Button appearance="ghost" variant="secondary" size="icon-sm" aria-label="Refresh">...</Button>
    </div>
  </AppShellCard.Header>
  <DataTable columns={columns} data={rows} />
</AppShellCard>
```

Use `AppShellCard.Actions` for compact non-data panel toolbar commands only.

**Detection**: Harness rule `ASC_HEADER_ACTIONS_002` catches Export, Refresh, and similar utility actions in right-side `AppShellCard.Actions` when the same card owns edge-to-edge table or chart content.

## 2026-06-25 · Executive KPI cockpit layout drift

**What broke**: Forge-generated KPI cockpit screens stacked two adjacent filter selects vertically on desktop, built KPI tiles from raw cards inside other cards, rendered summary metrics as plain bordered cells, placed Back/Export/notification controls in the body, and glued a drill-down table directly to the page container.

**Cause**: The output had access to the right components, but composed the page as generic cards and rows instead of using dashboard-specific primitives and AppShellCard toolbar slots.

**Rule**: Keep adjacent dashboard filters in a responsive row or grid. Use `MetricCard` for KPI tiles and summary metrics. Move Back or drill-down navigation into `AppShellCard.Header`; move Export, alert, and notification actions out of the body. For dense table/chart panels, use a compact action row under the title; for non-data panel toolbar commands, use `AppShellCard.Actions`. For app-page tables, use an inset `AppShellCard bodyPadding="none"` panel so the page has spacing while the `DataTable` remains edge-to-edge inside its card.

**Detection**: Harness rules `FILTER_LAYOUT_001`, `METRIC_CARD_001`, `ASC_HEADER_ACTIONS_001`, `ASC_HEADER_ACTIONS_002`, and `TABLE_CONTAINER_001` catch the structural cases. Visual review should still verify the final desktop density and table/container rhythm.

## 2026-06-24 · Standalone table pagination drifted

**What broke**: Generated tables rendered a standalone `<Pagination>` directly after table content inside a padded card body. The table appeared cramped, and pagination controls sat off-center under the table instead of reading as the table footer.

**Cause**: The output composed table chrome manually instead of using `DataTable` built-in pagination, then left the pagination controls unwrapped in the card body.

**Rule**: Prefer `<DataTable enablePagination ... />`. When a separate `<Pagination>` is required, place it in a same-width footer directly below the table:

```tsx
<div className="flex justify-center border-t border-border-subtle px-6 py-4">
  <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
</div>
```

**Never** leave `<Pagination>` as a bare sibling under a table inside default card padding.

**Detection**: Harness rule `ASC_PAGINATION_001` catches standalone table pagination that is not centered with the table. Visual: controls should sit centered under the table, not start at the left padding edge.

---

## 2026-04-28 · AppShellCard expand button drifts left when Header omitted

**What broke**: Expand/collapse button rendered flush-left in panels that had no `AppShellCard.Header`. Toolbar looked broken — expand sits where the title should be.

**Cause**: `AppShellCard` toolbar uses flex with the header taking the leading slot. When `AppShellCard.Header` is missing, there's nothing pushing actions/menu/expand to the right, so the auto-rendered expand collapses to the left edge.

**Rule**: **Always render `AppShellCard.Header`** (with at least `AppShellCard.Title`) inside `AppShellCard`. If you don't have a title, the panel probably shouldn't be using `AppShellCard` — use `AppShell.Content` directly or pick a different wrapper. No bare-body `AppShellCard`.

**Detection**: lint/codemod for `<AppShellCard>` without an `AppShellCard.Header` child. Visual: every panel screenshot should have expand button right-aligned.

---

## 2026-04-28 · DataTable wrapped in Card looks bad

**What broke**: Pages put a `<Card>` or padded `<AppShellCard>` around a `<DataTable>`. Result: double border, double padding, table cramped, scroll shadows fight card shadow.

**Cause**: `DataTable` already ships its own border, header, and scroll behavior. Wrapping it in another container that also has padding + border + shadow creates visual collision. The card "frame" duplicates what the table already provides.

**Rule**: **Don't wrap `DataTable` in `Card`.** Inside `AppShellCard`, set `bodyPadding="none"` so the table goes edge-to-edge and the card toolbar provides the chrome. Standalone, render `DataTable` directly with no card wrapper.

```tsx
// ❌ Wrong — double frame
<Card><DataTable ... /></Card>
<AppShellCard bodyPadding="md"><DataTable ... /></AppShellCard>  // padded body
<AppShellCard><DataTable ... /></AppShellCard>  // default padded body

// ✅ Right — card provides toolbar, table goes edge-to-edge
<AppShellCard bodyPadding="none">
  <AppShellCard.Header><AppShellCard.Title>Data</AppShellCard.Title></AppShellCard.Header>
  <DataTable ... />
</AppShellCard>

// ✅ Right — standalone, no wrapper needed
<DataTable ... />
```

**Detection**: grep for `<Card>...<DataTable` or `<AppShellCard>` containing `DataTable` without `bodyPadding="none"`. Visual: table should never have visible padding between its outer border and the card's inner edge.

---

## 2026-03-12 · Resizable size props: numbers vs strings

**What broke**: Layout collapsed on production deploy. Panels rendered at 20px instead of 20%.

**Cause**: `<ResizablePanel minSize={20} />` (number) treats value as **pixels**. To get 20%, must pass string: `<ResizablePanel minSize="20" />`.

**Rule** (from `CLAUDE.md`): Resizable size props (`defaultSize`, `minSize`, `maxSize`, `collapsedSize`) — numbers are pixels, strings are percentages. **Always strings for percentage sizing.**

**Detection**: visual regression test with viewport ≥ 1280px would catch the px-vs-% confusion.

---

## (template for future entries)

## YYYY-MM-DD · One-line title

**What broke**: user-visible symptom.

**Cause**: technical root cause.

**Rule**: enforced rule that prevents recurrence.

**Detection**: how to catch earlier (test, lint, type, review checklist).
