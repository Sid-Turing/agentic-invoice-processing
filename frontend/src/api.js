const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8010'

function buildForm({ message, conversationId, invoice, po }) {
  const fd = new FormData()
  fd.append('message', message || '')
  if (conversationId) fd.append('conversation_id', conversationId)
  if (invoice) fd.append('invoice', invoice)
  if (po) fd.append('po', po)
  return fd
}

/**
 * Stream a turn from POST /chat/stream, invoking handlers as SSE events arrive.
 * handlers: { onMeta, onTool, onToolResult, onToken, onDecision, onError, onDone }
 */
export async function streamMessage(payload, handlers = {}) {
  const resp = await fetch(`${API_BASE}/chat/stream`, { method: 'POST', body: buildForm(payload) })
  if (!resp.ok || !resp.body) {
    let detail = `HTTP ${resp.status}`
    try { const b = await resp.json(); if (b.detail) detail = b.detail } catch { /* ignore */ }
    handlers.onError?.({ detail })
    handlers.onDone?.()
    return
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''
  const dispatch = {
    meta: handlers.onMeta, tool: handlers.onTool, tool_result: handlers.onToolResult,
    token: handlers.onToken, decision: handlers.onDecision, error: handlers.onError,
    done: handlers.onDone,
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buf += decoder.decode(value, { stream: true })
    const blocks = buf.split('\n\n')
    buf = blocks.pop()
    for (const block of blocks) {
      let ev = null
      let data = null
      for (const line of block.split('\n')) {
        if (line.startsWith('event: ')) ev = line.slice(7)
        else if (line.startsWith('data: ')) {
          try { data = JSON.parse(line.slice(6)) } catch { data = null }
        }
      }
      if (ev && dispatch[ev]) dispatch[ev](data)
    }
  }
}

export async function getHealth() {
  const resp = await fetch(`${API_BASE}/health`)
  return resp.json()
}
