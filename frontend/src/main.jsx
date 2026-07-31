import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from '@humain/ui'
import App from './App.jsx'
// @humain/ui base + tokens + utilities first, then legacy page styles so
// existing (not-yet-migrated) pages keep their look during incremental migration.
import '@humain/ui/styles.css'
import './styles.css'
import './humain-overrides.css'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider defaultTheme="light">
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>,
)
