import { useState, useEffect, useCallback } from 'react'
import { getVendors } from '../api.js'

export default function VendorsPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [q, setQ] = useState('')

  const load = useCallback(async () => {
    setError(null)
    try { setData(await getVendors({ q })) } catch (e) { setError(e.message) }
  }, [q])
  useEffect(() => { load() }, [load])

  return (
    <>
      <header className="page-header">Vendors <small>reference data</small></header>
      <div className="page-body">
        <div className="toolbar">
          <input placeholder="Search vendor name…" value={q} onChange={(e) => setQ(e.target.value)} />
          <button onClick={load}>Refresh</button>
        </div>
        {error && <div className="error-state">⚠ {error}</div>}
        {!error && data && data.total === 0 && <div className="empty">No vendors.</div>}
        {!error && data && data.total > 0 && (
          <table className="grid">
            <thead><tr><th>Name</th><th>Tax ID</th><th>Address</th><th>State</th></tr></thead>
            <tbody>
              {data.items.map((v, i) => (
                <tr key={i}>
                  <td>{v.name || '—'}</td>
                  <td>{v.tax_id || '—'}</td>
                  <td>{v.address || '—'}</td>
                  <td>{v.state || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  )
}
