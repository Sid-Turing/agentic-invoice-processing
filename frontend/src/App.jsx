import { useState, useRef, useEffect } from 'react'
import { sendMessage } from './api.js'
import DecisionCard from './components/DecisionCard.jsx'

export default function App() {
  const [messages, setMessages] = useState([])
  const [conversationId, setConversationId] = useState(null)
  const [text, setText] = useState('')
  const [invoice, setInvoice] = useState(null)
  const [po, setPo] = useState(null)
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, loading])

  async function onSubmit(e) {
    e.preventDefault()
    if (loading) return
    if (!text.trim() && !invoice) return

    const attachments = [invoice?.name, po?.name].filter(Boolean)
    setMessages((m) => [...m, { role: 'user', text: text.trim(), attachments }])

    const payload = { message: text.trim(), conversationId, invoice, po }
    setText(''); setInvoice(null); setPo(null); setLoading(true)

    try {
      const data = await sendMessage(payload)
      setConversationId(data.conversation_id)
      setMessages((m) => [...m, { role: 'agent', text: data.message, decision: data.decision }])
    } catch (err) {
      setMessages((m) => [...m, { role: 'agent', text: '', error: err.message || String(err) }])
    } finally {
      setLoading(false)
    }
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); onSubmit(e) }
  }

  return (
    <div className="app">
      <header>
        Invoice Agent
        <small>upload an invoice (and optional PO) — the agent extracts, validates, reconciles, decides</small>
      </header>

      <main className="chat">
        {messages.length === 0 && (
          <div className="empty">Attach an invoice and hit Send, or ask a question.</div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            <div className="role">{m.role === 'user' ? 'You' : 'Agent'}</div>
            {m.text ? <div className="bubble">{m.text}</div> : null}
            {m.attachments?.length ? (
              <div className="attach">📎 {m.attachments.join(', ')}</div>
            ) : null}
            {m.error ? <div className="bubble error">⚠ {m.error}</div> : null}
            {m.decision ? <DecisionCard decision={m.decision} /> : null}
          </div>
        ))}
        {loading && <div className="msg agent"><div className="role">Agent</div><div className="bubble typing">Working…</div></div>}
        <div ref={endRef} />
      </main>

      <form className="composer" onSubmit={onSubmit}>
        <div className="files">
          <label>📄 Invoice: <span className="fname">{invoice?.name || 'none'}</span>
            <input type="file" accept=".pdf,.png,.jpg,.jpeg"
                   onChange={(e) => setInvoice(e.target.files[0] || null)} />
          </label>
          <label>📎 PO (optional): <span className="fname">{po?.name || 'none'}</span>
            <input type="file" accept=".pdf,.png,.jpg,.jpeg"
                   onChange={(e) => setPo(e.target.files[0] || null)} />
          </label>
        </div>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask something, or attach an invoice and hit Send…"
        />
        <button type="submit" disabled={loading}>{loading ? '…' : 'Send'}</button>
      </form>
    </div>
  )
}
