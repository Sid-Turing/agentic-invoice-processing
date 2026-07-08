import { NavLink } from 'react-router-dom'

const LINKS = [
  { to: '/', label: 'Chat', end: true },
  { to: '/history', label: 'History' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/purchase-orders', label: 'Purchase Orders' },
  { to: '/vendors', label: 'Vendors' },
]

export default function Sidebar() {
  return (
    <nav className="sidebar">
      <div className="brand">🧾 Invoice Agent</div>
      {LINKS.map((l) => (
        <NavLink
          key={l.to}
          to={l.to}
          end={l.end}
          className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}
        >
          {l.label}
        </NavLink>
      ))}
    </nav>
  )
}
