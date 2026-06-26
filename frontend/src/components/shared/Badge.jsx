import React from 'react'
import { SEVERITY_META, STATUS_META } from '../../utils/helpers'

export function SeverityBadge({ severity }) {
  const meta = SEVERITY_META[severity] || SEVERITY_META.healthy
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      padding: '3px 9px', borderRadius: 20,
      fontSize: 11, fontWeight: 600, letterSpacing: '0.04em',
      background: meta.bg, color: meta.color,
    }}>
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: meta.dot }} />
      {meta.label}
    </span>
  )
}

export function StatusBadge({ status }) {
  const meta = STATUS_META[status] || STATUS_META.operational
  return (
    <span style={{
      display: 'inline-block',
      padding: '3px 9px', borderRadius: 20,
      fontSize: 11, fontWeight: 600, letterSpacing: '0.04em',
      background: meta.bg, color: meta.color,
    }}>
      {meta.label}
    </span>
  )
}
