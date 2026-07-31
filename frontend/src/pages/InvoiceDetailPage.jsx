import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { PageHeader, DataTable, Button, EmptyState } from '@humain/ui'
import { ArrowLeft, FileText } from 'lucide-react'
import { getInvoice } from '../api.js'
import DecisionCard from '../components/DecisionCard.jsx'

const TOL = 0.02
const dash = (v) => (v === null || v === undefined || v === '' ? '—' : v)

const lineItemColumns = [
  { accessorKey: 'description', header: 'Description', cell: ({ getValue }) => dash(getValue()) },
  { accessorKey: 'quantity', header: 'Qty', cell: ({ getValue }) => dash(getValue()) },
  { accessorKey: 'unit_price', header: 'Unit price', cell: ({ getValue }) => dash(getValue()) },
  {
    id: 'tax_rate',
    header: 'Tax rate',
    cell: ({ row }) => {
      const r = row.original.tax_rate
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

function LineItems({ items }) {
  return (
    <div className="overflow-hidden rounded-lg border border-border bg-card">
      <DataTable
        columns={lineItemColumns}
        data={items ?? []}
        getRowId={(row, i) => String(i)}
        emptyState={<div className="p-4 text-sm text-muted-foreground">No line items.</div>}
      />
    </div>
  )
}

function FieldsCard({ fields }) {
  return (
    <div className="rounded-lg border border-border bg-card px-4 py-2">
      <dl className="grid grid-cols-1 gap-x-8 sm:grid-cols-2">
        {fields.map(([label, value]) => (
          <div
            key={label}
            className="flex items-center justify-between gap-3 border-b border-border-subtle py-2 text-sm"
          >
            <dt className="text-muted-foreground">{label}</dt>
            <dd className="text-secondary-foreground">{dash(value)}</dd>
          </div>
        ))}
      </dl>
    </div>
  )
}

function SectionTitle({ children }) {
  return <h2 className="mb-3 mt-6 text-base font-semibold">{children}</h2>
}

export default function InvoiceDetailPage() {
  const { recordId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let ok = true
    setData(null)
    setError(null)
    getInvoice(recordId)
      .then((d) => ok && setData(d))
      .catch((e) => ok && setError(e))
    return () => {
      ok = false
    }
  }, [recordId])

  const inv = data?.extracted_invoice || {}
  const title = data ? `Invoice ${inv.invoice_number || data.record_id.slice(0, 8)}` : 'Invoice'
  const subtitle = data ? `Processed ${new Date(data.created_at).toLocaleString()}` : undefined

  const decision = data && {
    verdict: data.verdict,
    reasons: data.reasons,
    checks: data.checks,
    explanation: data.explanation,
    matched_po: data.matched_po,
    record_id: data.record_id,
  }

  const fields = [
    ['Invoice #', inv.invoice_number],
    ['PO #', inv.po_number],
    ['Invoice date', inv.invoice_date],
    ['Due date', inv.due_date],
    ['Currency', inv.currency],
    ['Subtotal', inv.subtotal],
    ['Tax', inv.tax_amount],
    ['Total', inv.total_amount],
    ['Vendor', inv.vendor?.name],
    ['Customer', inv.customer?.name],
  ]

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <PageHeader title={title} supportingText={subtitle} showDivider className="px-3 py-2" />

      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-5 pr-5">
        <div className="mx-auto w-full">
          <Button
            appearance="ghost"
            variant="secondary"
            size="sm"
            onClick={() => navigate('/history')}
            startIcon={<ArrowLeft className="size-4" />}
          >
            Back to history
          </Button>

          {error ? (
            <div className="mt-4">
              <EmptyState
                title={error.status === 404 ? 'Record not found' : 'Couldn’t load invoice'}
                description={
                  error.status === 404
                    ? 'This invoice record does not exist.'
                    : error.message || 'Something went wrong.'
                }
                media="featured-icon"
                icon={<FileText />}
                primaryAction={{ label: 'Back to history', onClick: () => navigate('/history') }}
              />
            </div>
          ) : !data ? (
            <div className="mt-4 text-sm text-muted-foreground">Loading…</div>
          ) : (
            <div className="mt-4">
              <DecisionCard decision={decision} />

              {data.explanation && (
                <p className="mt-4 rounded-lg border border-border bg-muted px-4 py-3 text-sm text-secondary-foreground">
                  {data.explanation}
                </p>
              )}

              <SectionTitle>Extracted invoice</SectionTitle>
              <FieldsCard fields={fields} />

              <SectionTitle>Line items</SectionTitle>
              <LineItems items={inv.line_items} />

              {data.matched_po && (
                <>
                  <SectionTitle>
                    Matched purchase order — {data.matched_po.po_number} ({data.matched_po.source})
                  </SectionTitle>
                  <LineItems
                    items={(data.matched_po.line_items || []).map((li) => ({
                      ...li,
                      tax_rate: li.item_tax_rate,
                    }))}
                  />
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
