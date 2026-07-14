import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { authApi } from '../../api/services'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    first_name: '', last_name: '', email: '', password: '', confirm: '', phone: ''
  })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const handleChange = (e) => {
    setError(null)
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password !== form.confirm) {
      setError('Passwords do not match.')
      return
    }
    setLoading(true)
    try {
      await authApi.register({
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        password: form.password,
        phone: form.phone || undefined,
      })
      setSuccess(true)
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div style={styles.page}>
        <div style={styles.left}>
          <BrandPanel />
        </div>
        <div style={styles.right}>
          <div style={styles.card}>
            <div style={styles.successIcon}>✓</div>
            <h2 style={styles.cardTitle}>Account created</h2>
            <p style={styles.cardSub}>
              Your patient account is ready. Sign in to get started.
            </p>
            <button onClick={() => navigate('/login')} style={styles.btn}>
              Go to sign in
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={styles.page}>
      <div style={styles.left}>
        <BrandPanel />
      </div>
      <div style={styles.right}>
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Create your account</h2>
          <p style={styles.cardSub}>Patient registration. Doctors are added by their clinic.</p>

          <form onSubmit={handleSubmit} style={styles.form}>
            <div style={styles.row}>
              <div style={styles.col}>
                <label style={styles.label}>First name</label>
                <input name="first_name" required value={form.first_name} onChange={handleChange} style={styles.input} placeholder="Ana" />
              </div>
              <div style={styles.col}>
                <label style={styles.label}>Last name</label>
                <input name="last_name" required value={form.last_name} onChange={handleChange} style={styles.input} placeholder="López" />
              </div>
            </div>

            <label style={styles.label}>Email address</label>
            <input name="email" type="email" required value={form.email} onChange={handleChange} style={styles.input} placeholder="you@email.com" />

            <label style={styles.label}>Phone <span style={styles.optional}>(optional)</span></label>
            <input name="phone" type="tel" value={form.phone} onChange={handleChange} style={styles.input} placeholder="+48 000 000 000" />

            <label style={styles.label}>Password</label>
            <input name="password" type="password" required value={form.password} onChange={handleChange} style={styles.input} placeholder="At least 8 characters" />

            <label style={styles.label}>Confirm password</label>
            <input name="confirm" type="password" required value={form.confirm} onChange={handleChange} style={styles.input} placeholder="••••••••" />

            {error && <p style={styles.error}>{error}</p>}

            <button type="submit" disabled={loading} style={styles.btn}>
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <p style={styles.footer}>
            Already have an account?{' '}
            <Link to="/login" style={styles.link}>Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

function BrandPanel() {
  return (
    <div style={styles.leftInner}>
      <div style={styles.brand}>
        <span style={styles.brandIcon}>⊕</span>
        <span style={styles.brandName}>MedAssist</span>
      </div>
      <h1 style={styles.tagline}>Your health,<br />always accessible.</h1>
      <p style={styles.sub}>Create your patient account to join video consultations and view your appointment history.</p>
      <div style={styles.steps}>
        {[
          { n: '1', t: 'Create your account' },
          { n: '2', t: 'Your doctor connects with you' },
          { n: '3', t: 'Join consultations from anywhere' },
        ].map(s => (
          <div key={s.n} style={styles.step}>
            <span style={styles.stepNum}>{s.n}</span>
            <span style={styles.stepText}>{s.t}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

const styles = {
  page: { display: 'flex', minHeight: '100vh', fontFamily: "'Inter', system-ui, sans-serif", background: '#f8fafc' },
  left: { flex: 1, background: 'linear-gradient(145deg, #0f3460 0%, #16213e 60%, #0a1628 100%)', display: 'flex', alignItems: 'center', padding: '48px' },
  leftInner: { maxWidth: 480 },
  brand: { display: 'flex', alignItems: 'center', gap: 10, marginBottom: 56 },
  brandIcon: { fontSize: 28, color: '#4fc3f7' },
  brandName: { fontSize: 22, fontWeight: 700, color: '#fff', letterSpacing: '-0.3px' },
  tagline: { fontSize: 44, fontWeight: 700, color: '#fff', lineHeight: 1.15, letterSpacing: '-1.5px', margin: '0 0 20px 0' },
  sub: { fontSize: 17, color: '#94b8d4', lineHeight: 1.6, margin: '0 0 40px 0' },
  steps: { display: 'flex', flexDirection: 'column', gap: 16 },
  step: { display: 'flex', alignItems: 'center', gap: 14 },
  stepNum: { width: 28, height: 28, borderRadius: '50%', background: 'rgba(79,195,247,0.15)', border: '1px solid rgba(79,195,247,0.3)', color: '#4fc3f7', fontSize: 13, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 },
  stepText: { color: '#cbd5e1', fontSize: 15 },
  right: { width: 520, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '48px 32px' },
  card: { width: '100%', maxWidth: 420 },
  cardTitle: { fontSize: 28, fontWeight: 700, color: '#0f172a', letterSpacing: '-0.5px', margin: '0 0 8px 0' },
  cardSub: { fontSize: 14, color: '#64748b', margin: '0 0 28px 0' },
  form: { display: 'flex', flexDirection: 'column', gap: 4 },
  row: { display: 'flex', gap: 12 },
  col: { flex: 1, display: 'flex', flexDirection: 'column', gap: 4 },
  label: { fontSize: 13, fontWeight: 600, color: '#374151', marginTop: 10, marginBottom: 4 },
  optional: { fontWeight: 400, color: '#94a3b8' },
  input: { padding: '11px 14px', border: '1.5px solid #e2e8f0', borderRadius: 8, fontSize: 15, color: '#0f172a', background: '#fff', outline: 'none', fontFamily: 'inherit', width: '100%', boxSizing: 'border-box' },
  error: { background: '#fef2f2', border: '1px solid #fecaca', color: '#dc2626', borderRadius: 8, padding: '10px 14px', fontSize: 14, margin: '8px 0 0' },
  btn: { marginTop: 20, padding: '13px', background: '#0f3460', color: '#fff', border: 'none', borderRadius: 8, fontSize: 15, fontWeight: 600, cursor: 'pointer', letterSpacing: '-0.2px' },
  footer: { fontSize: 14, color: '#64748b', margin: '16px 0 0', textAlign: 'center' },
  link: { color: '#0f3460', fontWeight: 600, textDecoration: 'none' },
  successIcon: { width: 56, height: 56, borderRadius: '50%', background: '#dcfce7', border: '2px solid #86efac', color: '#16a34a', fontSize: 24, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 20 },
}
