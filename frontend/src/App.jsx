import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { AppShell, AppSidebar, SidebarProvider } from '@humain/ui'
import {
  MessageCircle,
  History,
  LayoutDashboard,
  ReceiptText,
  Store,
} from 'lucide-react'
import ChatPage from './pages/ChatPage.jsx'
import HistoryPage from './pages/HistoryPage.jsx'
import InvoiceDetailPage from './pages/InvoiceDetailPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import PurchaseOrdersPage from './pages/PurchaseOrdersPage.jsx'
import VendorsPage from './pages/VendorsPage.jsx'

const NAV = [
  { to: '/', label: 'Chat', icon: MessageCircle, end: true },
  { to: '/history', label: 'History', icon: History },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/purchase-orders', label: 'Purchase Orders', icon: ReceiptText },
  { to: '/vendors', label: 'Vendors', icon: Store },
]

// Wraps not-yet-migrated pages in the legacy full-bleed content column.
// Drop the wrapper from a route once its page is migrated to @humain/ui.
function LegacyPage({ children }) {
  return <div className="legacy-content">{children}</div>
}

function SidebarNav() {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isActive = (to, end) => (end ? pathname === to : pathname.startsWith(to))

  return (
    <AppSidebar
      logo={<span className="font-semibold">Invoice Agent</span>}
      logoSubtext="Enterprise Finance AI"
      collapsible="icon"
    >
      <AppSidebar.Nav>
        {NAV.map(({ to, label, icon: Icon, end }) => (
          <AppSidebar.NavItem
            key={to}
            icon={<Icon />}
            label={label}
            isActive={isActive(to, end)}
            onClick={() => navigate(to)}
          />
        ))}
      </AppSidebar.Nav>
      <AppSidebar.Account name="Alex Thompson" subtitle="Finance Lead" isOnline />
    </AppSidebar>
  )
}

export default function App() {
  return (
    // Edge-to-edge shell (no padding/gap) during migration: the not-yet-migrated
    // pages are full-bleed and expect the old `.content` column context. Re-enable
    // padded AppShellCard framing per-page as each screen is migrated.
    <AppShell.Root gap={0} padding={0} mobilePadding={0}>
      <AppShell.Sidebar>
        <SidebarProvider connected>
          <SidebarNav />
        </SidebarProvider>
      </AppShell.Sidebar>
      <AppShell.Panel flex={1} label="Main content">
        <Routes>
          {/* Migrated to @humain/ui — renders directly on the app canvas. */}
          <Route path="/" element={<ChatPage />} />
          <Route path="/vendors" element={<VendorsPage />} />
          <Route path="/purchase-orders" element={<PurchaseOrdersPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/history" element={<HistoryPage />} />
          {/* Not yet migrated — full-bleed legacy layout via `.legacy-content`. */}
          <Route path="/invoices/:recordId" element={<LegacyPage><InvoiceDetailPage /></LegacyPage>} />
        </Routes>
      </AppShell.Panel>
    </AppShell.Root>
  )
}
