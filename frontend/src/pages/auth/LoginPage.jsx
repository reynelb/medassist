import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import useAuthStore from '../../store/authStore'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, isLoading, error, clearError } = useAuthStore()
  const [form, setForm] = useState({ email: '', password: '' })

  const handleChange = (e) => {
    clearError()
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const role = await login(form.email, form.password)
      navigate(role === 'doctor' ? '/doctor/dashboard' : '/patient/home')
    } catch {}
  }

  return (
    <div style={styles.page}>
      <div style={styles.left}>
        <div style={styles.leftInner}>
          <div style={styles.brand}>
            <span style={styles.brandIcon}>⊕</span>
            <span style={styles.brandName}>MedAssist</span>
          </div>
          <div style={styles.taglineBlock}>
            <h1 style={styles.tagline}>The consultation,<br />reimagined.</h1>
            <p style={styles.sub}>Video calls, live transcription, and AI-generated reports — all in one place for modern medical teams.</p>
          </div>
          <div style={styles.pillRow}>
            {['Video consultations', 'Auto-transcription', 'AI report autofill'].map(t => (
              <span key={t} style={styles.pill}>{t}</span>
            ))}
          </div>
        </div>
      </div>

      <div style={styles.right}>
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Sign in</h2>
          <p style={styles.cardSub}>Welcome back. Enter your credentials to continue.</p>

          <form onSubmit={handleSubmit} style={styles.form}>
            <label style={styles.label}>Email address</label>
            <input
              name="email"
              type="email"
              required
              autoComplete="email"
              value={form.email}
              onChange={handleChange}
              style={styles.input}
              placeholder="you@clinic.com"
            />

            <label style={styles.label}>Password</label>
            <input
              name="password"
              type="password"
              required
              autoComplete="current-password"
              value={form.password}
              onChange={handleChange}
              style={styles.input}
              placeholder="••••••••"
            />

            {error && <p style={styles.error}>{error}</p>}

            <button type="submit" disabled={isLoading} style={styles.btn}>
              {isLoading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <p style={styles.footer}>
            New patient?{' '}
            <Link to="/register" style={styles.link}>Create an account</Link>
          </p>
          <p style={styles.footer}>
            Got an invite?{' '}
            <Link to="/register/invite/use" style={styles.link}>Register with invite</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

const styles = {
  page: {
    display: 'flex',
    minHeight: '100vh',
    fontFamily: "'Inter', system-ui, sans-serif",
    background: '#f8fafc',
  },
  left: {
    flex: 1,
    background: 'linear-gradient(145deg, #0f3460 0%, #16213e 60%, #0a1628 100%)',
    display: 'flex',
    alignItems: 'center',
    padding: '48px',
    '@media (max-width: 768px)': { display: 'none' },
  },
  leftInner: {
    maxWidth: 480,
  },
  brand: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    marginBottom: 64,
  },
  brandIcon: {
    fontSize: 28,
    color: '#4fc3f7',
  },
  brandName: {
    fontSize: 22,
    fontWeight: 700,
    color: '#ffffff',
    letterSpacing: '-0.3px',
  },
  taglineBlock: {
    marginBottom: 40,
  },
  tagline: {
    fontSize: 48,
    fontWeight: 700,
    color: '#ffffff',
    lineHeight: 1.15,
    letterSpacing: '-1.5px',
    margin: '0 0 20px 0',
  },
  sub: {
    fontSize: 17,
    color: '#94b8d4',
    lineHeight: 1.6,
    margin: 0,
  },
  pillRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 10,
  },
  pill: {
    background: 'rgba(79, 195, 247, 0.12)',
    border: '1px solid rgba(79, 195, 247, 0.25)',
    color: '#4fc3f7',
    borderRadius: 20,
    padding: '6px 14px',
    fontSize: 13,
    fontWeight: 500,
  },
  right: {
    width: 480,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '48px 32px',
  },
  card: {
    width: '100%',
    maxWidth: 380,
  },
  cardTitle: {
    fontSize: 28,
    fontWeight: 700,
    color: '#0f172a',
    letterSpacing: '-0.5px',
    margin: '0 0 8px 0',
  },
  cardSub: {
    fontSize: 15,
    color: '#64748b',
    margin: '0 0 32px 0',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
  },
  label: {
    fontSize: 13,
    fontWeight: 600,
    color: '#374151',
    marginTop: 12,
    marginBottom: 4,
  },
  input: {
    padding: '11px 14px',
    border: '1.5px solid #e2e8f0',
    borderRadius: 8,
    fontSize: 15,
    color: '#0f172a',
    background: '#fff',
    outline: 'none',
    transition: 'border-color 0.15s',
    fontFamily: 'inherit',
  },
  error: {
    background: '#fef2f2',
    border: '1px solid #fecaca',
    color: '#dc2626',
    borderRadius: 8,
    padding: '10px 14px',
    fontSize: 14,
    margin: '8px 0 0',
  },
  btn: {
    marginTop: 20,
    padding: '13px',
    background: '#0f3460',
    color: '#fff',
    border: 'none',
    borderRadius: 8,
    fontSize: 15,
    fontWeight: 600,
    cursor: 'pointer',
    letterSpacing: '-0.2px',
    transition: 'opacity 0.15s',
  },
  footer: {
    fontSize: 14,
    color: '#64748b',
    margin: '16px 0 0',
    textAlign: 'center',
  },
  link: {
    color: '#0f3460',
    fontWeight: 600,
    textDecoration: 'none',
  },
}
