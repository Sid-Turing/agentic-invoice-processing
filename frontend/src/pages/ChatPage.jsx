import { useState, useRef, useReducer, useEffect } from 'react'
import { streamMessage } from '../api.js'
import DecisionCard from '../components/DecisionCard.jsx'

function AgentTurn({ turn }) {
  return (
    <div className="msg agent">
      <div className="role">Agent</div>
      <div className="flow">
        {(turn.flow || []).map((item, i) => {
          if (item.type === 'tool') {
            return <div key={i} className="step"><span className="dot material-symbols-outlined">build</span> called <b>{item.name}</b></div>
          }
          if (item.type === 'result') {
            return (
              <div key={i} className="result">
                <span className={item.status === 'error' ? 'err' : 'ok'}>↳ {item.status || 'ok'}:</span> {item.output}
              </div>
            )
          }
          return <div key={i} className="tblock">{item.text}</div>
        })}
      </div>
      {turn.decision ? <DecisionCard decision={turn.decision} /> : null}
    </div>
  )
}

export default function ChatPage() {
  const [messages, setMessages] = useState([])
  const [conversationId, setConversationId] = useState(null)
  const [text, setText] = useState('')
  const [invoice, setInvoice] = useState(null)
  const [po, setPo] = useState(null)
  const [streaming, setStreaming] = useState(false)
  const liveRef = useRef(null)
  const [, tick] = useReducer((x) => x + 1, 0)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) })

  function appendToken(t) {
    const flow = liveRef.current.flow
    const last = flow[flow.length - 1]
    if (last && last.type === 'text') last.text += t.text
    else flow.push({ type: 'text', text: t.text })
    tick()
  }

  async function onSubmit(e) {
    e.preventDefault()
    if (streaming) return
    if (!text.trim() && !invoice) return

    const attachments = [invoice?.name, po?.name].filter(Boolean)
    setMessages((m) => [...m, { role: 'user', text: text.trim(), attachments }])

    const payload = { message: text.trim(), conversationId, invoice, po }
    setText(''); setInvoice(null); setPo(null)
    liveRef.current = { flow: [], decision: null }
    setStreaming(true)

    await streamMessage(payload, {
      onMeta: (d) => setConversationId(d.conversation_id),
      onTool: (d) => { liveRef.current.flow.push({ type: 'tool', name: d.name }); tick() },
      onToolResult: (d) => { liveRef.current.flow.push({ type: 'result', status: d.status, output: d.output }); tick() },
      onToken: (d) => appendToken(d),
      onDecision: (d) => { liveRef.current.decision = d; tick() },
      onError: (d) => { liveRef.current.flow.push({ type: 'text', text: '⚠ ' + (d?.detail || 'error') }); tick() },
      onDone: () => {
        const finished = liveRef.current || { flow: [], decision: null }
        liveRef.current = null
        setMessages((m) => [...m, { role: 'agent', flow: finished.flow, decision: finished.decision }])
        setStreaming(false)
      },
    })
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); onSubmit(e) }
  }

  const isEmpty = messages.length === 0 && !streaming

  return (
    <>
      <header className="page-header">
        Chat
        <small>Upload an invoice (and optional PO) — watch the agent extract, validate, reconcile, decide.</small>
      </header>

      <main className="chat">
        {isEmpty ? (
          <div className="empty-hero">
            <div className="hero-icon"><span className="material-symbols-outlined">upload_file</span></div>
            <h3>Awaiting Documents</h3>
            <p>Attach an invoice and hit Send, or ask a question. The agent extracts, validates, and reconciles in seconds.</p>
            <div className="quick-actions">
              <div className="qa-card">
                <span className="material-symbols-outlined">bolt</span>
                <div className="qa-title">Auto-extract data</div>
                <div className="qa-sub">Process header and line items instantly.</div>
              </div>
              <div className="qa-card">
                <span className="material-symbols-outlined">rebase_edit</span>
                <div className="qa-title">Reconcile with PO</div>
                <div className="qa-sub">Check for variance and matching errors.</div>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((m, i) =>
              m.role === 'user' ? (
                <div key={i} className="msg user">
                  <div className="role">You</div>
                  {m.text ? <div className="bubble">{m.text}</div> : null}
                  {m.attachments?.length ? <div className="attach">📎 {m.attachments.join(', ')}</div> : null}
                </div>
              ) : (
                <AgentTurn key={i} turn={m} />
              )
            )}
            {streaming && liveRef.current && <AgentTurn turn={liveRef.current} />}
          </>
        )}
        <div ref={endRef} />
      </main>

      <div className="composer">
        <form className="composer-inner" onSubmit={onSubmit}>
          <div className="status-row">
            <label className="status-item">
              <span className="material-symbols-outlined">description</span>
              Invoice: <span className="fname">{invoice?.name || 'none'}</span>
              <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={(e) => setInvoice(e.target.files[0] || null)} />
            </label>
            <label className="status-item">
              <span className="material-symbols-outlined">attachment</span>
              PO (optional): <span className="fname">{po?.name || 'none'}</span>
              <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={(e) => setPo(e.target.files[0] || null)} />
            </label>
          </div>

          <div className="chatbox">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder="Ask something, or attach an invoice and hit Send…"
              rows={1}
            />
            <div className="chatbox-actions">
              <button type="submit" className="send-btn" disabled={streaming}>
                {streaming ? '…' : <>Send <span className="material-symbols-outlined">send</span></>}
              </button>
            </div>
          </div>

          <p className="composer-note">Powered by Enterprise Finance AI. Confidential data is encrypted and secure.</p>
        </form>
      </div>
    </>
  )
}
