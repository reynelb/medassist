import { Link, useNavigate, useLocation } from 'react-router-dom'
import useAuthStore from '../../store/authStore'

const doctorNav = [
  { path: '/doctor/dashboard', label: 'Dashboard', icon: '⊞' },
  { path: '/doctor/patients', label: 'Patients', icon: '👤' },
  { path: '/doctor/appointments', label: 'Appointments', icon: '📅' },
  { path: '/doctor/invitations', label: 'Invitations', icon: '✉' },
  { path: '/doctor/profile', label: 'My Profile', icon: '⚙' },
]

const patientNav = [
  { path: '/patient/home', label: 'Home', icon: '⊞' },
  { path: '/patient/appointments', label: 'Appointments', icon: '📅' },
  { path: '/patient/doctor', label: 'My Doctor', icon: '👨‍⚕️' },
  { path: '/patient/profile', label: 'Profile', icon: '⚙' },
]

export default function Layout({ children }) {
  const { user, role, logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()
  const nav = role === 'doctor' ? doctorNav : patientNav

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div style={s.shell}>
      <aside style={s.sidebar}>
        <div style={s.brand}>
          <span style={s.brandIcon}>⊕</span>
          <span style={s.brandName}>MedAssist</span>
        </div>
        <nav style={s.nav}>
          {nav.map(item => (
            <Link
              key={item.path}
              to={item.path}
              style={{
                ...s.navItem,
                ...(location.pathname.startsWith(item.path) ? s.navActive : {}),
              }}
            >
              <span style={s.navIcon}>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
        <div style={s.sidebarFooter}>
          <div style={s.userRow}>
            <div style={s.avatar}>
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
            <div>
              <p style={s.userName}>{user?.first_name} {user?.last_name}</p>
              <p style={s.userRole}>{role === 'doctor' ? 'Doctor' : 'Patient'}</p>
            </div>
          </div>
          <button onClick={handleLogout} style={s.logoutBtn}>Sign out</button>
        </div>
      </aside>
      <main style={s.main}>{children}</main>
    </div>
  )
}

const s = {
  shell: { display: 'flex', minHeight: '100vh', fontFamily: "'Inter', system-ui, sans-serif", background: '#f8fafc' },
  sidebar: { width: 220, background: '#0f172a', display: 'flex', flexDirection: 'column', padding: '24px 0', flexShrink: 0, position: 'fixed', top: 0, bottom: 0, left: 0 },
  brand: { display: 'flex', alignItems: 'center', gap: 8, padding: '0 20px 32px' },
  brandIcon: { fontSize: 22, color: '#4fc3f7' },
  brandName: { fontSize: 16, fontWeight: 700, color: '#fff', letterSpacing: '-0.3px' },
  nav: { display: 'flex', flexDirection: 'column', gap: 2, flex: 1 },
  navItem: { display: 'flex', alignItems: 'center', gap: 10, padding: '10px 20px', color: '#94a3b8', fontSize: 14, fontWeight: 500, textDecoration: 'none', borderRadius: 0, transition: 'background 0.1s, color 0.1s' },
  navActive: { background: 'rgba(79,195,247,0.1)', color: '#4fc3f7', borderRight: '2px solid #4fc3f7' },
  navIcon: { fontSize: 15, width: 18, textAlign: 'center' },
  sidebarFooter: { padding: '16px 20px', borderTop: '1px solid rgba(255,255,255,0.08)' },
  userRow: { display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 },
  avatar: { width: 34, height: 34, borderRadius: '50%', background: '#1e3a5f', color: '#4fc3f7', fontSize: 12, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 },
  userName: { fontSize: 13, fontWeight: 600, color: '#f1f5f9', margin: 0 },
  userRole: { fontSize: 11, color: '#64748b', margin: 0, textTransform: 'capitalize' },
  logoutBtn: { width: '100%', padding: '8px', background: 'transparent', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 6, color: '#64748b', fontSize: 13, cursor: 'pointer' },
  main: { marginLeft: 220, flex: 1, padding: '32px', minWidth: 0 },
}
