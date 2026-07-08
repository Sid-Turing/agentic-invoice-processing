const TOL = 0.02

export default function LineItemsTable({ items }) {
  if (!items || items.length === 0) return <div className="muted">No line items.</div>
  return (
    <table className="grid">
      <thead>
        <tr><th>Description</th><th>Qty</th><th>Unit price</th><th>Tax rate</th><th>Total</th></tr>
      </thead>
      <tbody>
        {items.map((li, i) => {
          const expected = (li.quantity || 0) * (li.unit_price || 0)
          const mismatch = Math.abs(expected - (li.total_price || 0)) > TOL
          return (
            <tr key={i} className={mismatch ? 'row-flag' : ''}>
              <td>{li.description || '—'}</td>
              <td>{li.quantity ?? '—'}</td>
              <td>{li.unit_price ?? '—'}</td>
              <td>{li.tax_rate != null ? `${(li.tax_rate * 100).toFixed(3)}%` : '—'}</td>
              <td>{li.total_price ?? '—'}{mismatch ? ' ⚠' : ''}</td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}
