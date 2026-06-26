import React from 'react'

export default function Spinner({ size = 24, message = '' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, padding: 32 }}>
      <div style={{
        width: size, height: size,
        border: `2px solid var(--border)`,
        borderTopColor: 'var(--accent)',
        borderRadius: '50%',
        animation: 'spin 0.7s linear infinite',
      }} />
      {message && <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>{message}</p>}
    </div>
  )
}
