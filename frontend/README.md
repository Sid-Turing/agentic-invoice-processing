# Frontend — Agentic Invoice Processing

React + Vite UI for the backend. A collapsible sidebar, a top bar, and these routes:

- **Chat** (`/`) — upload invoice/PO, stream the agent's steps (tool calls, results,
  narration) live via `POST /chat/stream`, with a decision card and a live dashboard
  rail alongside.
- **History** (`/history`) — processed-invoice list (filter/search/paginate) → **detail** (`/invoices/:id`).
- **Dashboard** (`/dashboard`) — summary, aging, priority.
- **Purchase Orders** (`/purchase-orders`), **Vendors** (`/vendors`) — reference browsers.

## Setup

```bash
npm install
npm run dev                 # http://localhost:5173
npm run build               # production build (nginx-served in Docker)
```

## Configuration

- `VITE_API_BASE` — backend base URL (default `http://localhost:8010`). Set in `.env`
  for dev, or as a Docker build arg (baked into the bundle at build time).

## Layout

```
src/
  App.jsx                     shell: Sidebar + TopBar + routed pages
  api.js                      streamMessage() (SSE) + read helpers (getInvoices, getSummary, …)
  components/                 Sidebar, TopBar, DashboardRail, DecisionCard, LineItemsTable
  pages/                      ChatPage, HistoryPage, InvoiceDetailPage, DashboardPage,
                              PurchaseOrdersPage, VendorsPage
  styles.css
```
