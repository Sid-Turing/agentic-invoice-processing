import { useState, useEffect, useCallback } from 'react'
import { PageHeader, DataTable, Input, Button, EmptyState } from '@humain/ui'
import { Search, RefreshCw, ReceiptText, X } from 'lucide-react'
import { getPurchaseOrders, getPurchaseOrder } from '../api.js'

const TOL = 0.02
const dash = (v) => (v === null || v === undefined || v === '' ? '—' : v)

const columns = [
  { accessorKey: 'po_number', header: 'PO #' },
  { accessorKey: 'vendor_name', header: 'Vendor', cell: ({ getValue }) => dash(getValue()) },
  {
    id: 'total',
    header: 'Total',
    cell: ({ row }) => {
      const p = row.original
      return p.total_amount != null
        ? `${p.currency || ''} ${p.total_amount.toLocaleString()}`.trim()
        : '—'
    },
  },
  { accessorKey: 'po_date', header: 'PO date', cell: ({ getValue }) => dash(getValue()) },
  { accessorKey: 'due_date', header: 'Due', cell: ({ getValue }) => dash(getValue()) },
]

const lineItemColumns = [
  { accessorKey: 'description', header: 'Description', cell: ({ getValue }) => dash(getValue()) },
  { accessorKey: 'quantity', header: 'Qty', cell: ({ getValue }) => dash(getValue()) },
  { accessorKey: 'unit_price', header: 'Unit price', cell: ({ getValue }) => dash(getValue()) },
  {
    id: 'tax_rate',
    header: 'Tax rate',
    cell: ({ row }) => {
      const r = row.original.item_tax_rate
      return r != null ? `${(r * 100).toFixed(3)}%` : '—'
    },
  },
  {
    id: 'total',
    header: 'Total',
    cell: ({ row }) => {
      const li = row.original
      const expected = (li.quantity || 0) * (li.unit_price || 0)
      const mismatch = Math.abs(expected - (li.total_price || 0)) > TOL
      return (
        <span className={mismatch ? 'text-warning' : undefined}>
          {dash(li.total_price)}
          {mismatch ? ' ⚠' : ''}
        </span>
      )
    },
  },
]

export default function PurchaseOrdersPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [q, setQ] = useState('')
  const [openNo, setOpenNo] = useState(null)
  const [detail, setDetail] = useState(null)

  const load = useCallback(async () => {
    setError(null)
    try {
      setData(await getPurchaseOrders({ q }))
    } catch (e) {
      setError(e.message)
    }
  }, [q])
  useEffect(() => {
    load()
  }, [load])

  async function open(poNumber) {
    setOpenNo(poNumber)
    setDetail({ loading: true })
    try {
      setDetail(await getPurchaseOrder(poNumber))
    } catch (e) {
      setDetail({ error: e.message })
    }
  }
  function closeDetail() {
    setOpenNo(null)
    setDetail(null)
  }

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <PageHeader
        title="Purchase Orders"
        supportingText="Reference data"
        showDivider
        className="px-3 py-2"
      />

      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-5">
        <div className="mb-4 flex items-center gap-2">
          <Input
            className="max-w-md flex-1"
            placeholder="Search PO number..."
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
            title="Couldn't load purchase orders"
            description={error}
            media="featured-icon"
            icon={<ReceiptText />}
            primaryAction={{ label: 'Retry', onClick: load }}
          />
        ) : data && data.total === 0 ? (
          <EmptyState
            title="No purchase orders"
            description="No purchase orders match your search."
            media="featured-icon"
            icon={<ReceiptText />}
          />
        ) : (
          <DataTable
            columns={columns}
            data={data?.items ?? []}
            getRowId={(row) => row.po_number}
            onRowClick={(row) => open(row.original.po_number)}
            enableSorting
            enablePagination
            pageSize={10}
          />
        )}

        {openNo && (
          <div className="mt-6 rounded-lg border border-border bg-card p-4">
            <div className="mb-3 flex items-start gap-3">
              <div>
                <div className="text-lg font-semibold">
                  {(detail && detail.po_number) || openNo}
                  {detail?.vendor?.name ? ` — ${detail.vendor.name}` : ''}
                </div>
                {detail && !detail.loading && !detail.error && (
                  <div className="text-sm text-muted-foreground">
                    Total {detail.currency} {detail.total_amount} · status {detail.status || '—'}
                  </div>
                )}
              </div>
              <Button
                className="ml-auto"
                appearance="ghost"
                variant="secondary"
                size="icon-sm"
                onClick={closeDetail}
                aria-label="Close detail"
              >
                <X className="size-4" />
              </Button>
            </div>

            {detail?.loading && (
              <div className="text-sm text-muted-foreground">Loading PO…</div>
            )}
            {detail?.error && (
              <div className="text-sm text-destructive">⚠ {detail.error}</div>
            )}
            {detail && !detail.loading && !detail.error && (
              <DataTable
                columns={lineItemColumns}
                data={detail.line_items ?? []}
                getRowId={(row, i) => String(i)}
                emptyState={
                  <div className="p-4 text-sm text-muted-foreground">No line items.</div>
                }
              />
            )}
          </div>
        )}
      </div>
    </div>
  )
}
