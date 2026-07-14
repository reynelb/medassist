import Layout from '../../components/common/Layout'

// Fetch GET /doctors/me/profile — render editable form. PATCH /doctors/me/profile on save. Show preview of patient-facing card

export default function DoctorProfile() {
  return (
    <Layout>
      <div style={{ padding: '8px 0' }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: '#0f172a', letterSpacing: '-0.5px', margin: '0 0 8px 0' }}>
          My Profile
        </h1>
        <p style={{ color: '#64748b', fontSize: 14, margin: '0 0 32px 0' }}>
          🚧 This page is not yet implemented.
        </p>
        <div style={{ background: '#f8fafc', border: '1.5px dashed #e2e8f0', borderRadius: 12, padding: 32, color: '#94a3b8', fontSize: 13, lineHeight: 1.7 }}>
          <strong style={{ color: '#64748b' }}>Implementation note:</strong><br />
          Fetch GET /doctors/me/profile — render editable form. PATCH /doctors/me/profile on save. Show preview of patient-facing card
        </div>
      </div>
    </Layout>
  )
}
