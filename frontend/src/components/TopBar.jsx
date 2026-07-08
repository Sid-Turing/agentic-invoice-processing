import { useLocation } from 'react-router-dom'

const TITLES = {
  '/': 'New Invoice Reconciliation',
  '/history': 'Processed Invoices',
  '/dashboard': 'Overview',
  '/purchase-orders': 'Purchase Orders',
  '/vendors': 'Vendors',
}

export default function TopBar() {
  const { pathname } = useLocation()
  const label = TITLES[pathname] || (pathname.startsWith('/invoices/') ? 'Invoice Detail' : 'Session')
  return (
    <header className="topbar">
      <div className="crumbs">
        <span className="material-symbols-outlined">menu_open</span>
        <span className="cur">Current Session</span>
        <span className="sep">/</span>
        <span className="crumb">{label}</span>
      </div>
      <div className="topbar-actions">
        <button className="icon-btn" title="Notifications">
          <span className="material-symbols-outlined">notifications</span>
          <span className="dot" />
        </button>
        <button className="icon-btn" title="Help"><span className="material-symbols-outlined">help</span></button>
        <div className="avatar-sm">AT</div>
      </div>
    </header>
  )
}
