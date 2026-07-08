const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8010'

export async function sendMessage({ message, conversationId, invoice, po }) {
  const fd = new FormData()
  fd.append('message', message || '')
  if (conversationId) fd.append('conversation_id', conversationId)
  if (invoice) fd.append('invoice', invoice)
  if (po) fd.append('po', po)

  const resp = await fetch(`${API_BASE}/chat`, { method: 'POST', body: fd })
  if (!resp.ok) {
    let detail = `HTTP ${resp.status}`
    try {
      const body = await resp.json()
      if (body.detail) detail = body.detail
    } catch { /* ignore non-JSON error body */ }
    const err = new Error(detail)
    err.status = resp.status
    throw err
  }
  return resp.json()
}

export async function getHealth() {
  const resp = await fetch(`${API_BASE}/health`)
  return resp.json()
}
