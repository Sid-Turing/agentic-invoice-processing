import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  PageHeader,
  DataTable,
  Input,
  SelectRoot,
  SelectTrigger,
  SelectValue,
  SelectPopup,
  SelectItem,
  Button,
  Badge,
  Pagination,
  EmptyState,
} from '@humain/ui'
import { Search, RefreshCw, History as HistoryIcon } from 'lucide-react'
import { getInvoices } from '../api.js'

// Stable item maps (module-level) so the Select doesn't re-derive labels every render.
const VERDICT_ITEMS = { all: 'All verdicts', APPROVED: 'Approved', NEEDS_REVIEW: 'Needs review' }
const WINDOW_ITEMS = { all: 'All time', today: 'Today', '7d': 'Last 7 days', '30d': 'Last 30 days' }

const dash = (v) => (v === null || v === undefined || v === '' ? '—' : v)
const money = (v, cur) => (v == null ? '—' : `${cur || ''} ${Number(v).toLocaleString()}`.trim())
const when = (iso) => (iso ? new Date(iso).toLocaleString() : '—')
const verdictVariant = (v) =>
  v === 'APPROVED' ? 'success' : v === 'NEEDS_REVIEW' ? 'warning' : 'secondary'

const columns = [
  { accessorKey: 'invoice_number', header: 'Invoice #', cell: ({ getValue }) => dash(getValue()) },
  { accessorKey: 'vendor_name', header: 'Vendor', cell: ({ getValue }) => dash(getValue()) },
  {
    id: 'amount',
    header: 'Amount',
    cell: ({ row }) => money(row.original.total_amount, row.original.currency),
  },
  {
    accessorKey: 'verdict',
    header: 'Verdict',
    cell: ({ getValue }) => {
      const v = getValue()
      return <Badge variant={verdictVariant(v)}>{String(v).replace('_', ' ')}</Badge>
    },
  },
  {
    id: 'po',
    header: 'PO',
    cell: ({ row }) => {
      const r = row.original
      return r.matched_po_number ? `${r.matched_po_number} (${r.matched_po_source})` : '—'
    },
  },
  { id: 'processed', header: 'Processed', cell: ({ row }) => when(row.original.created_at) },
]

export default function HistoryPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [verdict, setVerdict] = useState('all')
  const [windowSel, setWindowSel] = useState('all')
  const [q, setQ] = useState('')
  const [page, setPage] = useState(1)
  const pageSize = 25
  const navigate = useNavigate()

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = { page, page_size: pageSize, window: windowSel, q }
      if (verdict !== 'all') params.verdict = verdict
      setData(await getInvoices(params))
    } catch (e) {
      setError(e.message || 'failed to load')
    } finally {
      setLoading(false)
    }
  }, [page, verdict, windowSel, q])

  useEffect(() => {
    load()
  }, [load])
  useEffect(() => {
    setPage(1)
  }, [verdict, windowSel, q])

  const total = data?.total ?? 0
  const pages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <PageHeader
        title="History"
        supportingText="Every processed invoice (per run)"
        showDivider
        className="px-3 py-2"
      />

      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-5 pr-5">
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <Input
            className="max-w-xs flex-1"
            placeholder="Search invoice #, vendor, PO..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
            startIcon={<Search className="size-4" />}
          />
          <SelectRoot value={verdict} onValueChange={setVerdict} items={VERDICT_ITEMS}>
            <SelectTrigger size="sm" className="w-44">
              <SelectValue placeholder="All verdicts" />
            </SelectTrigger>
            <SelectPopup alignItemWithTrigger={false} side="bottom" sideOffset={4}>
              <SelectItem value="all">All verdicts</SelectItem>
              <SelectItem value="APPROVED">Approved</SelectItem>
              <SelectItem value="NEEDS_REVIEW">Needs review</SelectItem>
            </SelectPopup>
          </SelectRoot>
          <SelectRoot value={windowSel} onValueChange={setWindowSel} items={WINDOW_ITEMS}>
            <SelectTrigger size="sm" className="w-44">
              <SelectValue placeholder="All time" />
            </SelectTrigger>
            <SelectPopup alignItemWithTrigger={false} side="bottom" sideOffset={4}>
              <SelectItem value="all">All time</SelectItem>
              <SelectItem value="today">Today</SelectItem>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
            </SelectPopup>
          </SelectRoot>
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
            title="Couldn't load history"
            description={error}
            media="featured-icon"
            icon={<HistoryIcon />}
            primaryAction={{ label: 'Retry', onClick: load }}
          />
        ) : loading ? (
          <div className="text-sm text-muted-foreground">Loading…</div>
        ) : total === 0 ? (
          <EmptyState
            title="No invoices match"
            description="Try adjusting your search or filters."
            media="featured-icon"
            icon={<HistoryIcon />}
          />
        ) : (
          <>
            <DataTable
              columns={columns}
              data={data.items}
              getRowId={(r) => r.record_id}
              onRowClick={(row) => navigate(`/invoices/${row.original.record_id}`)}
            />
            <div className="mt-4 flex flex-wrap items-center justify-center gap-4">
              <Pagination currentPage={page} totalPages={pages} onPageChange={setPage} />
              <span className="text-sm text-muted-foreground">{total} total</span>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
