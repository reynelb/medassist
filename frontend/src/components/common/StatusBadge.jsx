const colours = {
  scheduled:   { bg: '#eff6ff', color: '#1d4ed8', border: '#bfdbfe' },
  in_progress: { bg: '#fefce8', color: '#a16207', border: '#fde68a' },
  completed:   { bg: '#f0fdf4', color: '#15803d', border: '#bbf7d0' },
  cancelled:   { bg: '#fef2f2', color: '#dc2626', border: '#fecaca' },
  pending:     { bg: '#f8fafc', color: '#64748b', border: '#e2e8f0' },
  draft:       { bg: '#fefce8', color: '#a16207', border: '#fde68a' },
  confirmed:   { bg: '#f0fdf4', color: '#15803d', border: '#bbf7d0' },
  ready:       { bg: '#f0fdf4', color: '#15803d', border: '#bbf7d0' },
  failed:      { bg: '#fef2f2', color: '#dc2626', border: '#fecaca' },
}

export default function StatusBadge({ status }) {
  const c = colours[status] || colours.pending
  return (
    <span style={{
      display: 'inline-block',
      padding: '3px 10px',
      borderRadius: 20,
      fontSize: 12,
      fontWeight: 600,
      background: c.bg,
      color: c.color,
      border: `1px solid ${c.border}`,
      textTransform: 'capitalize',
    }}>
      {status?.replace('_', ' ')}
    </span>
  )
}
