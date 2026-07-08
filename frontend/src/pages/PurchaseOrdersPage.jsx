import { useState, useEffect, useCallback } from 'react'
import { getPurchaseOrders, getPurchaseOrder } from '../api.js'
import LineItemsTable from '../components/LineItemsTable.jsx'

export default function PurchaseOrdersPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [q, setQ] = useState('')
  const [selected, setSelected] = useState(null)

  const load = useCallback(async () => {
    setError(null)
    try { setData(await getPurchaseOrders({ q })) } catch (e) { setError(e.message) }
  }, [q])
  useEffect(() => { load() }, [load])

  async function open(poNumber) {
    setSelected({ loading: true })
    try { setSelected(await getPurchaseOrder(poNumber)) } catch (e) { setSelected({ error: e.message }) }
  }

  return (
    <>
      <header className="page-header">Purchase Orders <small>reference data</small></header>
      <div className="page-body">
        <div className="toolbar">
          <input placeholder="Search PO number…" value={q} onChange={(e) => setQ(e.target.value)} />
          <button onClick={load}>Refresh</button>
        </div>
        {error && <div className="error-state">⚠ {error}</div>}
        {!error && data && data.total === 0 && <div className="empty">No purchase orders.</div>}
        {!error && data && data.total > 0 && (
          <table className="grid">
            <thead><tr><th>PO #</th><th>Vendor</th><th>Total</th><th>PO date</th><th>Due</th></tr></thead>
            <tbody>
              {data.items.map((p) => (
                <tr key={p.po_number} className="row-link" onClick={() => open(p.po_number)}>
                  <td>{p.po_number}</td>
                  <td>{p.vendor_name || '—'}</td>
                  <td>{p.currency || ''} {p.total_amount?.toLocaleString() ?? '—'}</td>
                  <td>{p.po_date || '—'}</td>
                  <td>{p.due_date || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {selected && !selected.error && !selected.loading && (
          <div className="detail-panel">
            <h3>{selected.po_number} — {selected.vendor?.name || '—'}
              <button className="close" onClick={() => setSelected(null)}>✕</button>
            </h3>
            <div className="muted">Total {selected.currency} {selected.total_amount} · status {selected.status || '—'}</div>
            <LineItemsTable items={(selected.line_items || []).map((li) => ({ ...li, tax_rate: li.item_tax_rate }))} />
          </div>
        )}
        {selected?.loading && <div className="muted">Loading PO…</div>}
        {selected?.error && <div className="error-state">⚠ {selected.error}</div>}
      </div>
    </>
  )
}
