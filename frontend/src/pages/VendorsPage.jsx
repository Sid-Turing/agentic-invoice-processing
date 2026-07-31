import { useState, useEffect, useCallback } from 'react'
import { PageHeader, DataTable, Input, Button, EmptyState } from '@humain/ui'
import { Search, RefreshCw, Store } from 'lucide-react'
import { getVendors } from '../api.js'

const dash = (v) => v || '—'

const columns = [
  { accessorKey: 'name', header: 'Name', cell: ({ getValue }) => dash(getValue()) },
  { accessorKey: 'tax_id', header: 'Tax ID', cell: ({ getValue }) => dash(getValue()) },
  { accessorKey: 'address', header: 'Address', cell: ({ getValue }) => dash(getValue()) },
  { accessorKey: 'state', header: 'State', cell: ({ getValue }) => dash(getValue()) },
]

export default function VendorsPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [q, setQ] = useState('')

  const load = useCallback(async () => {
    setError(null)
    try {
      setData(await getVendors({ q }))
    } catch (e) {
      setError(e.message)
    }
  }, [q])
  useEffect(() => {
    load()
  }, [load])

  const items = data?.items ?? []

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <PageHeader
        title="Vendors"
        supportingText="Reference data"
        showDivider
        className="px-3 py-2"
      />

      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-5 pr-5">
        <div className="mb-4 flex items-center gap-2">
          <Input
            className="max-w-md flex-1"
            placeholder="Search vendor name..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
            startIcon={<Search className="size-4" />}
          />
          <Button
            appearance="outline"
            variant="secondary"
            size="sm"
            onClick={load}
            startIcon={<RefreshCw className="size-4" />}
          >
            Refresh
          </Button>
        </div>

        {error ? (
          <EmptyState
            title="Couldn't load vendors"
            description={error}
            media="featured-icon"
            icon={<Store />}
            primaryAction={{ label: 'Retry', onClick: load }}
          />
        ) : items.length === 0 ? (
          <EmptyState
            title="No vendors"
            description="No vendor reference data matches your search."
            media="featured-icon"
            icon={<Store />}
          />
        ) : (
          <DataTable
            columns={columns}
            data={items}
            getRowId={(row, i) => `${i}-${row.name ?? ''}`}
            enableSorting
            enablePagination
            pageSize={10}
          />
        )}
      </div>
    </div>
  )
}
