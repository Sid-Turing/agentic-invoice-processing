import { useState, useEffect } from 'react'
import { PageHeader, DataTable, MetricCard, Progress, Badge, EmptyState } from '@humain/ui'
import { LayoutDashboard } from 'lucide-react'
import { getSummary } from '../api.js'

const BUCKET_LABEL = {
  overdue: 'Overdue',
  due_today: 'Due today',
  due_1_7: 'Due 1–7d',
  due_8_14: 'Due 8–14d',
  due_15_plus: 'Due 15+d',
  undated: 'Undated',
}

const dash = (v) => (v === null || v === undefined || v === '' ? '—' : v)

// overdue → destructive, due_soon → warning, everything else → secondary
const reasonVariant = (r) =>
  r === 'overdue' ? 'destructive' : r === 'due_soon' ? 'warning' : 'secondary'

const priorityColumns = [
  { accessorKey: 'invoice_number', header: 'Invoice #', cell: ({ getValue }) => dash(getValue()) },
  { accessorKey: 'vendor_name', header: 'Vendor', cell: ({ getValue }) => dash(getValue()) },
  {
    id: 'amount',
    header: 'Amount',
    cell: ({ row }) => {
      const p = row.original
      return p.total_amount != null
        ? `${p.currency || ''} ${p.total_amount.toLocaleString()}`.trim()
        : '—'
    },
  },
  { accessorKey: 'due_date', header: 'Due', cell: ({ getValue }) => dash(getValue()) },
  {
    id: 'why',
    header: 'Why',
    cell: ({ row }) => (
      <div className="flex flex-wrap gap-2">
        {(row.original.reasons || []).map((r) => (
          <Badge key={r} variant={reasonVariant(r)}>
            {r.replace('_', ' ')}
          </Badge>
        ))}
      </div>
    ),
  },
]

export default function DashboardPage() {
  const [s, setS] = useState(null)
  const [error, setError] = useState(null)

  const load = () => {
    setError(null)
    getSummary().then(setS).catch((e) => setError(e.message))
  }
  useEffect(() => {
    load()
  }, [])

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <PageHeader
        title="Dashboard"
        supportingText="Processing summary & analytics"
        showDivider
        className="px-3 py-2"
      />

      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-5">
        {error ? (
          <EmptyState
            title="Couldn't load dashboard"
            description={error}
            media="featured-icon"
            icon={<LayoutDashboard />}
            primaryAction={{ label: 'Retry', onClick: load }}
          />
        ) : !s ? (
          <div className="text-sm text-muted-foreground">Loading…</div>
        ) : (
          <>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-5">
              <MetricCard title="Processed" value={s.total_processed} />
              <MetricCard title="Approved" value={s.approved_count} />
              <MetricCard title="Needs review" value={s.needs_review_count} />
              <MetricCard
                title="Approved amount"
                value={s.total_approved_amount}
                valueFormatter={(n) => `$ ${n.toLocaleString()}`}
              />
              <MetricCard title="Processed today" value={s.processed_today} />
            </div>

            <section className="mt-6">
              <h3 className="mb-3 text-base font-semibold">Aging</h3>
              <div className="flex flex-col gap-3">
                {s.aging.map((b) => (
                  <div key={b.bucket} className="flex items-center gap-3">
                    <span className="w-24 text-sm text-muted-foreground">
                      {BUCKET_LABEL[b.bucket] || b.bucket}
                    </span>
                    <Progress className="flex-1" value={Math.min(100, b.count)} />
                    <span className="w-8 text-right text-sm">{b.count}</span>
                  </div>
                ))}
              </div>
            </section>

            <section className="mt-6">
              <h3 className="mb-3 text-base font-semibold">Priority ({s.priority.length})</h3>
              {s.priority.length === 0 ? (
                <div className="text-sm text-muted-foreground">
                  Nothing high-value and overdue.
                </div>
              ) : (
                <DataTable
                  columns={priorityColumns}
                  data={s.priority}
                  getRowId={(p) => p.record_id}
                  enableSorting
                />
              )}
            </section>
          </>
        )}
      </div>
    </div>
  )
}
