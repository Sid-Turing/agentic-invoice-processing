import { useState, useEffect } from 'react'
import { getSummary } from '../api.js'

const BUCKET_LABEL = {
  overdue: 'Overdue', due_today: 'Due today', due_1_7: 'Due 1–7d',
  due_8_14: 'Due 8–14d', due_15_plus: 'Due 15+d', undated: 'Undated',
}
const AGING_MAX = 100

export default function DashboardRail({ refreshKey }) {
  const [s, setS] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let ok = true
    getSummary().then((d) => ok && setS(d)).catch((e) => ok && setError(e.message))
    return () => { ok = false }
  }, [refreshKey])

  return (
    <aside className="chat-rail">
      <div className="rail-title">Dashboard</div>
      {error && <div className="error-state">⚠ {error}</div>}
      {!error && !s && <div className="muted">Loading…</div>}
      {!error && s && (
        <>
          <div className="rail-stats">
            <div className="rail-stat"><div className="v">{s.total_processed}</div><div className="l">Processed</div></div>
            <div className="rail-stat"><div className="v">{s.approved_count}</div><div className="l">Approved</div></div>
            <div className="rail-stat"><div className="v">{s.needs_review_count}</div><div className="l">Needs review</div></div>
            <div className="rail-stat"><div className="v">{s.processed_today}</div><div className="l">Today</div></div>
            <div className="rail-stat wide"><div className="v">$ {s.total_approved_amount.toLocaleString()}</div><div className="l">Approved amount</div></div>
          </div>

          <div className="rail-section-title">Aging</div>
          <div className="rail-aging">
            {s.aging.map((b) => (
              <div className="aging-row" key={b.bucket}>
                <span className="aging-label">{BUCKET_LABEL[b.bucket]}</span>
                <span className="aging-track"><span className="aging-fill" style={{ width: `${Math.min(100, (b.count / AGING_MAX) * 100)}%` }} /></span>
                <span className="aging-count">{b.count}</span>
              </div>
            ))}
          </div>

          <div className="rail-section-title">Priority ({s.priority.length})</div>
          {s.priority.length === 0 ? (
            <div className="muted" style={{ fontSize: 12 }}>Nothing high-value and overdue.</div>
          ) : (
            <div className="rail-prio">
              {s.priority.slice(0, 6).map((p) => (
                <div className="rail-prio-item" key={p.record_id}>
                  <div className="top">
                    <span>{p.invoice_number || '—'}</span>
                    <span className="amt">{p.currency || ''} {p.total_amount?.toLocaleString()}</span>
                  </div>
                  <div className="sub">
                    <span>{p.vendor_name || '—'}</span>
                    {p.reasons.map((r) => <span key={r} className={`tag tag-${r}`}>{r.replace('_', ' ')}</span>)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </aside>
  )
}
