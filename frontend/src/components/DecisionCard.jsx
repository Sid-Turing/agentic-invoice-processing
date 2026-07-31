import { Badge } from '@humain/ui'

const CHECK = {
  pass: { label: 'PASS', variant: 'success' },
  fail: { label: 'FAIL', variant: 'destructive' },
  skipped: { label: 'SKIP', variant: 'secondary' },
}
const verdictVariant = (v) =>
  v === 'APPROVED' ? 'success' : v === 'NEEDS_REVIEW' ? 'warning' : 'secondary'

export default function DecisionCard({ decision }) {
  if (!decision) return null
  const { verdict, reasons = [], checks = [], matched_po, record_id } = decision
  return (
    <div className="mt-3 overflow-hidden rounded-lg border border-border bg-card">
      <div className="flex flex-wrap items-center gap-2 border-b border-border-subtle px-4 py-3">
        <Badge variant={verdictVariant(verdict)}>{verdict.replace('_', ' ')}</Badge>
        <span className="text-sm text-muted-foreground">
          {matched_po
            ? `PO ${matched_po.po_number} (${matched_po.source})`
            : 'no PO — reconciliation skipped'}
          {record_id ? ` · record ${record_id.slice(0, 8)}` : ''}
        </span>
      </div>

      {reasons.length > 0 && (
        <div className="flex flex-wrap gap-1 px-4 pt-3">
          {reasons.map((r, i) => (
            <Badge key={i} variant="destructive" size="sm">
              {r.code}
            </Badge>
          ))}
        </div>
      )}

      <ul className="flex flex-col gap-2 px-4 py-3">
        {checks.map((c, i) => {
          const meta = CHECK[c.status] || { label: c.status, variant: 'secondary' }
          return (
            <li key={i} className="flex items-baseline gap-2 text-sm">
              <Badge variant={meta.variant} size="sm">
                {meta.label}
              </Badge>
              <span className="text-secondary-foreground">{c.id}</span>
              {c.detail ? <span className="text-muted-foreground">{c.detail}</span> : null}
            </li>
          )
        })}
      </ul>
    </div>
  )
}
