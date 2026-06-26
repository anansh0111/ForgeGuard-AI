import React from 'react'

export default function Card({ children, title, subtitle, style = {}, noPad = false }) {
  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-lg)',
      ...style,
    }}>
      {(title || subtitle) && (
        <div style={{
          padding: '16px 20px 12px',
          borderBottom: '1px solid var(--border)',
        }}>
          {title && <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{title}</div>}
          {subtitle && <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>{subtitle}</div>}
        </div>
      )}
      <div style={noPad ? {} : { padding: 20 }}>
        {children}
      </div>
    </div>
  )
}
