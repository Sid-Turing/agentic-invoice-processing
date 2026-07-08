import { useState, useEffect } from 'react'
import { getSummary } from '../api.js'

const BUCKET_LABEL = {
  overdue: 'Overdue', due_today: 'Due today', due_1_7: 'Due 1–7d',
  due_8_14: 'Due 8–14d', due_15_plus: 'Due 15+d', undated: 'Undated',
}

function Stat({ label, value }) {
  return <div className="stat"><div className="stat-value">{value}</div><div className="stat-label">{label}</div></div>
}

export default function DashboardPage() {
  const [s, setS] = useState(null)
  const [error, setError] = useState(null)

  const load = () => { setError(null); getSummary().then(setS).catch((e) => setError(e.message)) }
  useEffect(() => { load() }, [])

  if (error) return <><header className="page-header">Dashboard</header><div className="page-body"><div className="error-state">⚠ {error} <button onClick={load}>Retry</button></div></div></>
  if (!s) return <><header className="page-header">Dashboard</header><div className="page-body muted">Loading…</div></>

  const AGING_MAX = 100  // fixed scale: bar width = count% (clamped)

  return (
    <>
      <header className="page-header">Dashboard <small>processing summary &amp; analytics</small></header>
      <div className="page-body">
        <div className="stats">
          <Stat label="Processed" value={s.total_processed} />
          <Stat label="Approved" value={s.approved_count} />
          <Stat label="Needs review" value={s.needs_review_count} />
          <Stat label="Approved amount" value={`$ ${s.total_approved_amount.toLocaleString()}`} />
          <Stat label="Processed today" value={s.processed_today} />
        </div>

        <section className="panel">
          <div className="panel-head"><h3>Aging</h3></div>
          <div className="panel-body aging-list">
            {s.aging.map((b) => (
              <div className="aging-row" key={b.bucket}>
                <span className="aging-label">{BUCKET_LABEL[b.bucket]}</span>
                <span className="aging-track">
                  <span className="aging-fill" style={{ width: `${Math.min(100, (b.count / AGING_MAX) * 100)}%` }} />
                </span>
                <span className="aging-count">{b.count}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-head"><h3>Priority ({s.priority.length})</h3></div>
          {s.priority.length === 0 ? (
            <div className="panel-body empty">Nothing high-value and overdue.</div>
          ) : (
            <table className="grid grid-flush">
              <thead><tr><th>Invoice #</th><th>Vendor</th><th>Amount</th><th>Due</th><th>Why</th></tr></thead>
              <tbody>
                {s.priority.map((p) => (
                  <tr key={p.record_id}>
                    <td>{p.invoice_number || '—'}</td>
                    <td>{p.vendor_name || '—'}</td>
                    <td>{p.currency || ''} {p.total_amount?.toLocaleString()}</td>
                    <td>{p.due_date || '—'}</td>
                    <td>{p.reasons.map((r) => <span key={r} className={`tag tag-${r}`}>{r.replace('_', ' ')}</span>)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </div>
    </>
  )
}
