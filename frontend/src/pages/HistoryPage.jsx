import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getInvoices } from '../api.js'

const money = (v, cur) => (v == null ? '—' : `${cur || ''} ${Number(v).toLocaleString()}`.trim())
const when = (iso) => (iso ? new Date(iso).toLocaleString() : '—')

export default function HistoryPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [verdict, setVerdict] = useState('')
  const [windowSel, setWindowSel] = useState('all')
  const [q, setQ] = useState('')
  const [page, setPage] = useState(1)
  const pageSize = 25
  const navigate = useNavigate()

  const load = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const params = { page, page_size: pageSize, window: windowSel, q }
      if (verdict) params.verdict = verdict
      setData(await getInvoices(params))
    } catch (e) {
      setError(e.message || 'failed to load')
    } finally {
      setLoading(false)
    }
  }, [page, verdict, windowSel, q])

  useEffect(() => { load() }, [load])
  useEffect(() => { setPage(1) }, [verdict, windowSel, q])

  const total = data?.total ?? 0
  const pages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <>
      <header className="page-header">History <small>every processed invoice (per run)</small></header>
      <div className="page-body">
        <div className="toolbar">
          <input placeholder="Search invoice #, vendor, PO…" value={q} onChange={(e) => setQ(e.target.value)} />
          <select value={verdict} onChange={(e) => setVerdict(e.target.value)}>
            <option value="">All verdicts</option>
            <option value="APPROVED">Approved</option>
            <option value="NEEDS_REVIEW">Needs review</option>
          </select>
          <select value={windowSel} onChange={(e) => setWindowSel(e.target.value)}>
            <option value="all">All time</option>
            <option value="today">Today</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
          </select>
          <button onClick={load}>Refresh</button>
        </div>

        {error && <div className="error-state">⚠ {error} <button onClick={load}>Retry</button></div>}
        {!error && loading && <div className="muted">Loading…</div>}
        {!error && !loading && total === 0 && <div className="empty">No invoices match.</div>}

        {!error && total > 0 && (
          <>
            <table className="grid">
              <thead>
                <tr><th>Invoice #</th><th>Vendor</th><th>Amount</th><th>Verdict</th><th>PO</th><th>Processed</th></tr>
              </thead>
              <tbody>
                {data.items.map((r) => (
                  <tr key={r.record_id} className="row-link" onClick={() => navigate(`/invoices/${r.record_id}`)}>
                    <td>{r.invoice_number || '—'}</td>
                    <td>{r.vendor_name || '—'}</td>
                    <td>{money(r.total_amount, r.currency)}</td>
                    <td><span className={`pill ${r.verdict}`}>{r.verdict.replace('_', ' ')}</span></td>
                    <td>{r.matched_po_number ? `${r.matched_po_number} (${r.matched_po_source})` : '—'}</td>
                    <td>{when(r.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="pager">
              <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>‹ Prev</button>
              <span>Page {page} / {pages} · {total} total</span>
              <button disabled={page >= pages} onClick={() => setPage((p) => p + 1)}>Next ›</button>
            </div>
          </>
        )}
      </div>
    </>
  )
}
