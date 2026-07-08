import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getInvoice } from '../api.js'
import DecisionCard from '../components/DecisionCard.jsx'
import LineItemsTable from '../components/LineItemsTable.jsx'

function Field({ label, value }) {
  return <div className="field"><span className="k">{label}</span><span className="v">{value ?? '—'}</span></div>
}

export default function InvoiceDetailPage() {
  const { recordId } = useParams()
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let ok = true
    setData(null); setError(null)
    getInvoice(recordId).then((d) => ok && setData(d)).catch((e) => ok && setError(e))
    return () => { ok = false }
  }, [recordId])

  if (error) {
    return (
      <>
        <header className="page-header">Invoice</header>
        <div className="page-body">
          <div className="error-state">{error.status === 404 ? 'Record not found.' : `⚠ ${error.message}`}</div>
          <Link className="nav-back" to="/history">← Back to history</Link>
        </div>
      </>
    )
  }
  if (!data) return <><header className="page-header">Invoice</header><div className="page-body muted">Loading…</div></>

  const inv = data.extracted_invoice || {}
  const decision = {
    verdict: data.verdict, reasons: data.reasons, checks: data.checks,
    explanation: data.explanation, matched_po: data.matched_po, record_id: data.record_id,
  }

  return (
    <>
      <header className="page-header">
        Invoice {inv.invoice_number || data.record_id.slice(0, 8)}
        <small>processed {new Date(data.created_at).toLocaleString()}</small>
      </header>
      <div className="page-body">
        <Link className="nav-back" to="/history">← Back to history</Link>

        <DecisionCard decision={decision} />

        {data.explanation && <p className="explanation">{data.explanation}</p>}

        <h3>Extracted invoice</h3>
        <div className="fields">
          <Field label="Invoice #" value={inv.invoice_number} />
          <Field label="PO #" value={inv.po_number} />
          <Field label="Invoice date" value={inv.invoice_date} />
          <Field label="Due date" value={inv.due_date} />
          <Field label="Currency" value={inv.currency} />
          <Field label="Subtotal" value={inv.subtotal} />
          <Field label="Tax" value={inv.tax_amount} />
          <Field label="Total" value={inv.total_amount} />
          <Field label="Vendor" value={inv.vendor?.name} />
          <Field label="Customer" value={inv.customer?.name} />
        </div>

        <h3>Line items</h3>
        <LineItemsTable items={inv.line_items} />

        {data.matched_po && (
          <>
            <h3>Matched purchase order — {data.matched_po.po_number} ({data.matched_po.source})</h3>
            <LineItemsTable items={(data.matched_po.line_items || []).map((li) => ({
              ...li, tax_rate: li.item_tax_rate,
            }))} />
          </>
        )}
      </div>
    </>
  )
}
