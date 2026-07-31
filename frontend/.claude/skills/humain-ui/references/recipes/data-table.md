# DataTable Recipe

**Use:** DataTable, DropdownMenu, Badge, Avatar, SortableHeader
**Optional:** Button, Progress

When a `DataTable` is the primary body of an `AppShellCard`, render it directly inside `AppShellCard bodyPadding="none"`. Put the label and context in `AppShellCard.Header`, not in duplicated body headings. If the table has Export, Refresh, alert, notification, or other utility actions, place them inside `AppShellCard.Header` below the title/subtitle as a compact wrapped action row, not in right-side `AppShellCard.Actions`. Use `DataTable` built-in pagination with `enablePagination` when possible; if you must compose standalone `Pagination` below a table, center it in a same-width footer instead of leaving it unwrapped in the card body. On full app pages, put the table in `<AppShellCard inset bodyPadding="none">` rather than rendering a bare `DataTable` or flush table card directly inside `AppShell.Panel`. For list pages with search or filters, keep controls together in one padded responsive toolbar between the header and table; do not repeat the title/count in the body.

```tsx
<AppShellCard inset bodyPadding="none">
  <AppShellCard.Header>
    <AppShellCard.Title>Team members</AppShellCard.Title>
    <AppShellCard.Subtitle>Manage roles, teams, and status</AppShellCard.Subtitle>
    <div className="mt-3 flex flex-wrap items-center gap-2">
      <Button appearance="outline" variant="secondary" size="sm">Export</Button>
      <Button appearance="ghost" variant="secondary" size="icon-sm" aria-label="Refresh">...</Button>
    </div>
  </AppShellCard.Header>
  <div className="border-b border-border-subtle px-6 py-4">
    <div className="grid grid-cols-1 gap-3 md:grid-cols-[minmax(0,320px)_repeat(2,minmax(180px,1fr))]">
      <Input placeholder="Search members..." startIcon={<Search className="size-4" />} />
      <Select placeholder="All roles" />
      <Select placeholder="All statuses" />
    </div>
  </div>
  <DataTable columns={columns} data={teamMembers} getRowId={(row) => row.id} enablePagination />
</AppShellCard>
```

```tsx
import { useState } from 'react'
import {
  DataTable,
  type ColumnDef,
  type RowSelectionState,
  type SortingState,
  type PaginationState,
  SortableHeader,
  Badge,
  Avatar,
  Button,
  DropdownMenu,
  Input,
  Select
} from '@humain/ui'
import { MoreHorizontal, Mail, Search } from 'lucide-react'

// Define your data type
interface TeamMember {
  id: string
  name: string
  email: string
  role: string
  status: 'Active' | 'Inactive'
  teams: string[]
  avatar?: string
}

// Sample data
const teamMembers: TeamMember[] = [
  {
    id: '1',
    name: 'Olivia Rhye',
    email: 'olivia@company.com',
    role: 'Product Designer',
    status: 'Active',
    teams: ['Design', 'Product'],
    avatar: 'https://i.pravatar.cc/150?u=olivia'
  },
  {
    id: '2',
    name: 'Phoenix Baker',
    email: 'phoenix@company.com',
    role: 'Product Manager',
    status: 'Active',
    teams: ['Product', 'Marketing'],
    avatar: 'https://i.pravatar.cc/150?u=phoenix'
  },
  {
    id: '3',
    name: 'Lana Steiner',
    email: 'lana@company.com',
    role: 'Frontend Developer',
    status: 'Inactive',
    teams: ['Engineering'],
    avatar: 'https://i.pravatar.cc/150?u=lana'
  },
]

// Define columns with different cell types
const columns: ColumnDef<TeamMember, unknown>[] = [
  {
    accessorKey: 'name',
    header: ({ column }) => <SortableHeader column={column}>Name</SortableHeader>,
    cell: ({ row }) => (
      <div className="flex items-center gap-3">
        <Avatar src={row.original.avatar} alt={row.original.name} fallback={row.original.name} size="sm" />
        <div className="flex flex-col">
          <span className="text-sm font-medium text-foreground">{row.original.name}</span>
          <span className="text-sm text-secondary-foreground">@{row.original.email.split('@')[0]}</span>
        </div>
      </div>
    ),
  },
  {
    accessorKey: 'status',
    header: ({ column }) => <SortableHeader column={column}>Status</SortableHeader>,
    cell: ({ row }) => (
      <Badge variant="dot" color={row.original.status === 'Active' ? 'success' : 'secondary'} size="sm">
        {row.original.status}
      </Badge>
    ),
  },
  {
    accessorKey: 'role',
    header: ({ column }) => <SortableHeader column={column}>Role</SortableHeader>,
    cell: ({ row }) => <span className="text-sm text-secondary-foreground">{row.original.role}</span>,
  },
  {
    accessorKey: 'teams',
    header: 'Teams',
    enableSorting: false,
    cell: ({ row }) => (
      <div className="flex items-center gap-1">
        {row.original.teams.slice(0, 2).map((team) => (
          <Badge key={team} color="primary" variant="outline" size="sm">{team}</Badge>
        ))}
        {row.original.teams.length > 2 && (
          <Badge color="secondary" variant="outline" size="sm">+{row.original.teams.length - 2}</Badge>
        )}
      </div>
    ),
  },
  {
    id: 'actions',
    header: '',
    enableSorting: false,
    cell: ({ row }) => (
      <div className="flex items-center gap-2 justify-end">
        <Button appearance="ghost" variant="secondary" size="icon-sm" iconOnly aria-label="Email member"><Mail className="size-4" /></Button>
        <DropdownMenu>
          <DropdownMenu.Trigger render={<Button appearance="ghost" variant="secondary" size="icon-sm" iconOnly aria-label="Open row actions"><MoreHorizontal className="size-4" /></Button>} />
          <DropdownMenu.Popup align="end">
            <DropdownMenu.Item onSelect={() => console.log('Edit', row.original.id)}>Edit</DropdownMenu.Item>
            <DropdownMenu.Item onSelect={() => console.log('View', row.original.id)}>View profile</DropdownMenu.Item>
            <DropdownMenu.Item className="text-destructive" onSelect={() => console.log('Delete', row.original.id)}>Delete</DropdownMenu.Item>
          </DropdownMenu.Popup>
        </DropdownMenu>
      </div>
    ),
    meta: { cellClassName: 'w-24' },
  },
]

function TeamMembersTable() {
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({})
  const [sorting, setSorting] = useState<SortingState>([{ id: 'name', desc: false }])
  const [pagination, setPagination] = useState<PaginationState>({ pageIndex: 0, pageSize: 10 })
  const [searchQuery, setSearchQuery] = useState('')

  const filteredData = teamMembers.filter(
    (member) =>
      member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      member.email.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const selectedCount = Object.keys(rowSelection).length

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
          <Input
            placeholder="Search members..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            startIcon={<Search className="size-4" />}
            className="w-full sm:w-64"
          />
          {selectedCount > 0 && (
            <span className="text-sm text-secondary-foreground">{selectedCount} selected</span>
          )}
        </div>
        {selectedCount > 0 && (
          <div className="flex flex-wrap gap-2">
            <Button appearance="outline" variant="secondary" size="sm">Export</Button>
            <Button appearance="solid" variant="destructive" size="sm">Delete</Button>
          </div>
        )}
      </div>

      <DataTable
        columns={columns}
        data={filteredData}
        getRowId={(row) => row.id}
        enableRowSelection
        enableMultiRowSelection
        rowSelection={rowSelection}
        onRowSelectionChange={setRowSelection}
        showSelectAll
        enableSorting
        sorting={sorting}
        onSortingChange={setSorting}
        sortingMode="client"
        enablePagination
        pagination={pagination}
        onPaginationChange={setPagination}
        paginationMode="client"
        paginationType="page-default"
        dividers="line"
        density="default"
        rounded="all"
        bordered
        onRowClick={(row) => console.log('Row clicked:', row.original)}
        emptyState={
          <div className="py-8 text-center">
            <p className="text-secondary-foreground mb-4">No team members found</p>
            <Button appearance="solid" variant="primary" size="sm">Add team member</Button>
          </div>
        }
      />
    </div>
  )
}
```

**Key props:**
- `columns`: ColumnDef array with accessorKey, header (string or SortableHeader), cell (render function)
- `data`: Array of row data matching your type
- `getRowId`: Recommended function to get stable row IDs; falls back to row index when omitted

**Row Selection:** enableRowSelection, enableMultiRowSelection, rowSelection, onRowSelectionChange, showSelectAll
**Sorting:** enableSorting, sorting, onSortingChange, sortingMode ('client' | 'server')
**Pagination:** enablePagination, pagination, onPaginationChange, paginationMode ('client' | 'server'), pageSize, paginationType. Prefer built-in `DataTable` pagination; center any standalone `Pagination` under the table with a same-width `flex justify-center` footer.
**Column Filtering:** enableColumnFilters, columnFilters, onColumnFiltersChange, filteringMode
**Styling:** dividers ('line' | 'alternating'), density ('default' | 'compact'), rounded, bordered
**Advanced:** maxHeight, stickyHeader, stickyFirstColumn, virtualization, loading, error, emptyState
