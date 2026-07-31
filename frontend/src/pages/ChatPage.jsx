import { useState, useRef, useReducer } from 'react'
import { PageHeader, AIContainer, AIMessage, AIToolCall, AIEmptyState, Button } from '@humain/ui'
import { Upload, Paperclip, Send, Zap, GitCompare } from 'lucide-react'
import { streamMessage } from '../api.js'
import DecisionCard from '../components/DecisionCard.jsx'
import DashboardRail from '../components/DashboardRail.jsx'

// Render-time only: pair each streamed `tool` item with its following `result`
// item into a single tool-call part for AIToolCall. Does not mutate flow state.
function toToolParts(flow) {
  const out = []
  for (let i = 0; i < flow.length; i++) {
    const item = flow[i]
    if (item.type === 'tool') {
      const next = flow[i + 1]
      let status = 'running'
      let result
      let error
      if (next && next.type === 'result') {
        if (next.status === 'error') {
          status = 'error'
          error = next.output
        } else {
          status = 'success'
          result = next.output
        }
        i += 1 // consume the paired result
      }
      out.push({ kind: 'tool', id: String(out.length), toolName: item.name, status, result, error })
    } else if (item.type === 'result') {
      out.push({
        kind: 'tool',
        id: String(out.length),
        toolName: 'result',
        status: item.status === 'error' ? 'error' : 'success',
        result: item.output,
      })
    } else {
      out.push({ kind: 'text', id: String(out.length), text: item.text })
    }
  }
  return out
}

function AgentTurn({ turn }) {
  const parts = toToolParts(turn.flow || [])
  return (
    <div className="flex flex-col gap-2">
      {parts.map((p) =>
        p.kind === 'tool' ? (
          <AIToolCall
            key={p.id}
            toolPart={{
              toolCallId: p.id,
              toolName: p.toolName,
              result: p.result,
              error: p.error,
              status: p.status,
            }}
          />
        ) : (
          <AIMessage key={p.id} type="received" isAgent senderName="Agent" content={p.text} />
        )
      )}
      {turn.decision ? <DecisionCard decision={turn.decision} /> : null}
    </div>
  )
}

function FeatureCard({ icon, title, sub }) {
  return (
    <div className="chat-feature-card rounded-xl border border-border bg-card p-4 text-left transition-colors">
      <div className="inline-flex items-center justify-center rounded-lg bg-muted p-2 text-primary">
        {icon}
      </div>
      <div className="mt-3 text-sm font-medium">{title}</div>
      <div className="mt-1 text-xs text-muted-foreground">{sub}</div>
    </div>
  )
}

function EmptyHero() {
  return (
    <AIEmptyState
      icon={
        <div className="flex size-14 items-center justify-center rounded-2xl bg-muted text-primary">
          <Upload className="size-6" />
        </div>
      }
      title="Awaiting Documents"
      description="Attach an invoice and hit Send, or ask a question. The agent extracts, validates, and reconciles in seconds."
    >
      <div className="mt-6 grid w-full max-w-xl grid-cols-1 gap-3 sm:grid-cols-2">
        <FeatureCard
          icon={<Zap className="size-4" />}
          title="Auto-extract data"
          sub="Process header and line items instantly."
        />
        <FeatureCard
          icon={<GitCompare className="size-4" />}
          title="Reconcile with PO"
          sub="Check for variance and matching errors."
        />
      </div>
    </AIEmptyState>
  )
}

export default function ChatPage() {
  const [messages, setMessages] = useState([])
  const [conversationId, setConversationId] = useState(null)
  const [text, setText] = useState('')
  const [invoice, setInvoice] = useState(null)
  const [po, setPo] = useState(null)
  const [streaming, setStreaming] = useState(false)
  const [railKey, setRailKey] = useState(0)
  const liveRef = useRef(null)
  const [tickCount, tick] = useReducer((x) => x + 1, 0)

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
    setText('')
    setInvoice(null)
    setPo(null)
    liveRef.current = { flow: [], decision: null }
    setStreaming(true)

    await streamMessage(payload, {
      onMeta: (d) => setConversationId(d.conversation_id),
      onTool: (d) => {
        liveRef.current.flow.push({ type: 'tool', name: d.name })
        tick()
      },
      onToolResult: (d) => {
        liveRef.current.flow.push({ type: 'result', status: d.status, output: d.output })
        tick()
      },
      onToken: (d) => appendToken(d),
      onDecision: (d) => {
        liveRef.current.decision = d
        tick()
      },
      onError: (d) => {
        liveRef.current.flow.push({ type: 'text', text: '⚠ ' + (d?.detail || 'error') })
        tick()
      },
      onDone: () => {
        const finished = liveRef.current || { flow: [], decision: null }
        liveRef.current = null
        setMessages((m) => [...m, { role: 'agent', flow: finished.flow, decision: finished.decision }])
        setStreaming(false)
        if (finished.decision) setRailKey((k) => k + 1) // refresh dashboard rail
      },
    })
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSubmit(e)
    }
  }

  const isEmpty = messages.length === 0 && !streaming

  return (
    <div className="flex h-full overflow-hidden">
      <div className="flex min-w-0 flex-1 flex-col">
        <PageHeader
          title="Chat"
          supportingText="Upload an invoice (and optional PO) — watch the agent extract, validate, reconcile, decide."
          showDivider
          className="px-3 py-2"
        />

        <AIContainer className="min-h-0 flex-1">
          <AIContainer.Messages autoScrollKey={`${messages.length}:${tickCount}`} className="w-full max-w-full">
            {isEmpty ? (
              <EmptyHero />
            ) : (
              <div className="mx-auto flex w-full flex-col gap-4 px-4 py-4">
                {messages.map((m, i) =>
                  m.role === 'user' ? (
                    <div key={i} className="flex flex-col gap-1">
                      {m.text ? <AIMessage type="sent" content={m.text} /> : null}
                      {m.attachments?.length ? (
                        <div className="pl-1 text-xs text-muted-foreground">
                          📎 {m.attachments.join(', ')}
                        </div>
                      ) : null}
                    </div>
                  ) : (
                    <AgentTurn key={i} turn={m} />
                  )
                )}
                {streaming && liveRef.current && <AgentTurn turn={liveRef.current} />}
              </div>
            )}
          </AIContainer.Messages>
        </AIContainer>

        <form onSubmit={onSubmit} className="border-t border-border-subtle p-3">
          <div className="mx-auto">
            <div className="chat-composer rounded-2xl border border-border bg-card px-3 py-2 transition-colors">
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder="Ask something, or attach an invoice and hit Send…"
                rows={3}
                style={{ minHeight: 96, maxHeight: 240 }}
                className="w-full resize-none border-0 bg-transparent px-1 py-1 text-sm text-secondary-foreground outline-none focus:outline-none"
              />

              <div className="mt-1 flex items-center gap-2">
                <label
                  title="Upload invoice"
                  className={
                    'chat-upload inline-flex cursor-pointer items-center gap-2 rounded-lg px-2 py-1 text-xs transition-colors ' +
                    (invoice ? 'text-primary' : 'text-secondary-foreground')
                  }
                >
                  <Upload className="size-4" />
                  <span className="truncate" style={{ maxWidth: 160 }}>
                    {invoice ? invoice.name : 'Invoice'}
                  </span>
                  <input
                    type="file"
                    accept=".pdf,.png,.jpg,.jpeg"
                    className="hidden"
                    onChange={(e) => setInvoice(e.target.files[0] || null)}
                  />
                </label>
                <label
                  title="Upload PO (optional)"
                  className={
                    'chat-upload inline-flex cursor-pointer items-center gap-2 rounded-lg px-2 py-1 text-xs transition-colors ' +
                    (po ? 'text-primary' : 'text-secondary-foreground')
                  }
                >
                  <Paperclip className="size-4" />
                  <span className="truncate" style={{ maxWidth: 160 }}>
                    {po ? po.name : 'PO (optional)'}
                  </span>
                  <input
                    type="file"
                    accept=".pdf,.png,.jpg,.jpeg"
                    className="hidden"
                    onChange={(e) => setPo(e.target.files[0] || null)}
                  />
                </label>

                <div className="flex-1" />

                <Button
                  type="button"
                  size="sm"
                  onClick={onSubmit}
                  disabled={streaming}
                  endIcon={streaming ? undefined : <Send className="size-4" />}
                >
                  {streaming ? '…' : 'Send'}
                </Button>
              </div>
            </div>

            <p className="mt-2 text-center text-xs text-muted-foreground">
              Powered by Enterprise Finance AI. Confidential data is encrypted and secure.
            </p>
          </div>
        </form>
      </div>

      <DashboardRail refreshKey={railKey} />
    </div>
  )
}
