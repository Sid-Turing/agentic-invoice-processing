import { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar.jsx'
import TopBar from './components/TopBar.jsx'
import ChatPage from './pages/ChatPage.jsx'
import HistoryPage from './pages/HistoryPage.jsx'
import InvoiceDetailPage from './pages/InvoiceDetailPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import PurchaseOrdersPage from './pages/PurchaseOrdersPage.jsx'
import VendorsPage from './pages/VendorsPage.jsx'

export default function App() {
  const [collapsed, setCollapsed] = useState(false)
  return (
    <div className={'app-shell' + (collapsed ? ' collapsed' : '')}>
      <Sidebar />
      <div className="content">
        <TopBar onToggle={() => setCollapsed((c) => !c)} />
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/invoices/:recordId" element={<InvoiceDetailPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/purchase-orders" element={<PurchaseOrdersPage />} />
          <Route path="/vendors" element={<VendorsPage />} />
        </Routes>
      </div>
    </div>
  )
}
