const STATUS_LABEL = { pass: 'PASS', fail: 'FAIL', skipped: 'SKIP' }

export default function DecisionCard({ decision }) {
  if (!decision) return null
  const { verdict, reasons = [], checks = [], matched_po, record_id } = decision
  return (
    <div className="card">
      <div className="card-top">
        <span className={`pill ${verdict}`}>{verdict.replace('_', ' ')}</span>
        <span className="meta">
          {matched_po
            ? `PO ${matched_po.po_number} (${matched_po.source})`
            : 'no PO — reconciliation skipped'}
          {record_id ? ` · record ${record_id.slice(0, 8)}` : ''}
        </span>
      </div>

      {reasons.length > 0 && (
        <div className="reasons">
          {reasons.map((r, i) => (
            <span key={i} className="reason">{r.code}</span>
          ))}
        </div>
      )}

      <ul className="checks">
        {checks.map((c, i) => (
          <li key={i}>
            <span className={`st ${c.status}`}>{STATUS_LABEL[c.status] || c.status}</span>
            <span className="cname">{c.id}</span>
            {c.detail ? <span className="cdetail">{c.detail}</span> : null}
          </li>
        ))}
      </ul>
    </div>
  )
}
