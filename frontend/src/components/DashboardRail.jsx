import { useState, useEffect, useRef } from 'react'
import { Progress, Badge } from '@humain/ui'
import { GripVertical } from 'lucide-react'
import { getSummary } from '../api.js'

const BUCKET_LABEL = {
  overdue: 'Overdue',
  due_today: 'Due today',
  due_1_7: 'Due 1–7d',
  due_8_14: 'Due 8–14d',
  due_15_plus: 'Due 15+d',
  undated: 'Undated',
}
const reasonVariant = (r) =>
  r === 'overdue' ? 'destructive' : r === 'due_soon' ? 'warning' : 'secondary'

// Resizable-width constraints for the rail.
const MIN_W = 300
const MAX_W = 560
const DEFAULT_W = 360
const STORAGE_KEY = 'dashboardRailWidth'

// Drag-to-resize width, persisted to localStorage so it survives navigation/reload.
function useResizableWidth() {
  const [width, setWidth] = useState(() => {
    try {
      const saved = Number(localStorage.getItem(STORAGE_KEY))
      if (saved >= MIN_W && saved <= MAX_W) return saved
    } catch {
      /* ignore */
    }
    return DEFAULT_W
  })
  const widthRef = useRef(width)
  widthRef.current = width
  const dragging = useRef(false)
  const startX = useRef(0)
  const startW = useRef(0)

  useEffect(() => {
    function onMove(e) {
      if (!dragging.current) return
      // Rail is on the right, so dragging the handle left widens it.
      const delta = startX.current - e.clientX
      const next = Math.min(MAX_W, Math.max(MIN_W, startW.current + delta))
      widthRef.current = next
      setWidth(next)
    }
    function onUp() {
      if (!dragging.current) return
      dragging.current = false
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
      try {
        localStorage.setItem(STORAGE_KEY, String(widthRef.current))
      } catch {
        /* ignore */
      }
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    return () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
  }, [])

  const onHandleMouseDown = (e) => {
    dragging.current = true
    startX.current = e.clientX
    startW.current = widthRef.current
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
    e.preventDefault()
  }

  return { width, onHandleMouseDown }
}

function Stat({ value, label }) {
  return (
    <div className="rounded-lg border border-border bg-card p-3">
      <div className="text-xl font-semibold tracking-tight">{value}</div>
      <div className="mt-1 text-xs text-muted-foreground">{label}</div>
    </div>
  )
}

export default function DashboardRail({ refreshKey }) {
  const [s, setS] = useState(null)
  const [error, setError] = useState(null)
  const { width, onHandleMouseDown } = useResizableWidth()

  useEffect(() => {
    let ok = true
    getSummary()
      .then((d) => ok && setS(d))
      .catch((e) => ok && setError(e.message))
    return () => {
      ok = false
    }
  }, [refreshKey])

  return (
    <aside
      className="relative hidden shrink-0 border-l border-border lg:flex"
      style={{ width }}
    >
      <div
        className="dashboard-resize-handle"
        role="separator"
        aria-orientation="vertical"
        aria-label="Resize dashboard panel"
        onMouseDown={onHandleMouseDown}
      >
        <span className="dashboard-resize-grip">
          <GripVertical className="size-3" />
        </span>
      </div>

      <div className="min-w-0 flex-1 overflow-y-auto bg-app p-5">
        <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Dashboard
        </div>
        {error && <div className="text-sm text-destructive">⚠ {error}</div>}
        {!error && !s && <div className="text-sm text-muted-foreground">Loading…</div>}
        {!error && s && (
          <>
            <div className="grid grid-cols-2 gap-2">
              <Stat value={s.total_processed} label="Processed" />
              <Stat value={s.approved_count} label="Approved" />
              <Stat value={s.needs_review_count} label="Needs review" />
              <Stat value={s.processed_today} label="Today" />
              <div className="col-span-2">
                <Stat value={`$ ${s.total_approved_amount.toLocaleString()}`} label="Approved amount" />
              </div>
            </div>

            <div className="mb-2 mt-5 text-sm font-semibold">Aging</div>
            <div className="flex flex-col gap-2">
              {s.aging.map((b) => (
                <div key={b.bucket} className="flex items-center gap-2">
                  <span className="w-16 shrink-0 text-xs text-muted-foreground">
                    {BUCKET_LABEL[b.bucket] || b.bucket}
                  </span>
                  <Progress className="flex-1" value={Math.min(100, b.count)} />
                  <span className="w-6 shrink-0 text-right text-xs">{b.count}</span>
                </div>
              ))}
            </div>

            <div className="mb-2 mt-5 text-sm font-semibold">Priority ({s.priority.length})</div>
            {s.priority.length === 0 ? (
              <div className="text-xs text-muted-foreground">Nothing high-value and overdue.</div>
            ) : (
              <div className="flex flex-col gap-2">
                {s.priority.slice(0, 6).map((p) => (
                  <div key={p.record_id} className="rounded-lg border border-border bg-card p-3">
                    <div className="flex items-center justify-between gap-2 text-sm">
                      <span>{p.invoice_number || '—'}</span>
                      <span className="font-semibold">
                        {p.currency || ''} {p.total_amount?.toLocaleString()}
                      </span>
                    </div>
                    <div className="mt-1 flex flex-wrap items-center gap-1 text-xs text-muted-foreground">
                      <span>{p.vendor_name || '—'}</span>
                      {p.reasons.map((r) => (
                        <Badge key={r} variant={reasonVariant(r)} size="sm">
                          {r.replace('_', ' ')}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </aside>
  )
}
