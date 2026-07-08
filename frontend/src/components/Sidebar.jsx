import { NavLink } from 'react-router-dom'

const LINKS = [
  { to: '/', label: 'Chat', icon: 'chat', end: true },
  { to: '/history', label: 'History', icon: 'history' },
  { to: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
  { to: '/purchase-orders', label: 'Purchase Orders', icon: 'receipt_long' },
  { to: '/vendors', label: 'Vendors', icon: 'store' },
]

function Icon({ name }) {
  return <span className="material-symbols-outlined">{name}</span>
}

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-box"><span className="material-symbols-outlined">description</span></div>
        <div>
          <div className="brand-name">Invoice Agent</div>
          <div className="brand-sub">Enterprise Finance AI</div>
        </div>
      </div>

      <nav className="nav">
        {LINKS.map((l) => (
          <NavLink key={l.to} to={l.to} end={l.end}
                   className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            <Icon name={l.icon} />
            <span>{l.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="user-card">
        <div className="avatar">AT</div>
        <div className="user-meta">
          <div className="user-name">Alex Thompson</div>
          <div className="user-role">Finance Lead</div>
        </div>
        <span className="material-symbols-outlined">settings</span>
      </div>
    </aside>
  )
}
