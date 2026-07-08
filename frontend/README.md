# Agentic Invoice Frontend

A minimal ChatGPT-style React (Vite) UI for the **agentic-invoice-processing**
backend. Upload an invoice (and optionally a PO), and see the agent's reply plus a
structured decision card (verdict, reasons, per-check trace). Uses the backend's
non-streaming `POST /chat` endpoint.

## Prerequisites

- Node 18+
- The backend running (see the `agentic-invoice-processing` repo). By default this
  app calls `http://localhost:8010`.

## Setup

```bash
npm install
cp .env.example .env        # optional — set VITE_API_BASE if the backend isn't on :8010
npm run dev                 # http://localhost:5173
```

## Configuration

- `VITE_API_BASE` — backend base URL (default `http://localhost:8010`). The backend
  enables permissive CORS for local development.

## Build

```bash
npm run build && npm run preview
```

## Structure

```
src/
  main.jsx                  # React entry
  App.jsx                   # chat state + composer (files + message), multi-turn conversation_id
  api.js                    # sendMessage() -> POST /chat (multipart)
  components/DecisionCard.jsx  # verdict pill + reasons + per-check trace
  styles.css
```
