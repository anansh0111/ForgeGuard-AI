import React from 'react'
import { SeverityBadge } from '../shared/Badge'
import { formatProb, timeAgo } from '../../utils/helpers'

function getSeverity(prob) {
  if (prob > 0.9) return 'critical'
  if (prob > 0.7) return 'warning'
  if (prob > 0.5) return 'inspection'
  return 'healthy'
}

export default function RecentPredictions({ predictions }) {
  const recent = predictions?.slice(0, 8) || []
  if (!recent.length) return (
    <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>No predictions yet — simulator warming up.</p>
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {recent.map(p => (
        <div key={p.id} style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '10px 4px',
          borderBottom: '1px solid var(--border)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent)', minWidth: 64 }}>
              {p.machine_id}
            </span>
            <SeverityBadge severity={getSeverity(p.failure_probability)} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{
              fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 600,
              color: p.failure_probability > 0.7 ? 'var(--critical)' : p.failure_probability > 0.5 ? 'var(--warning)' : 'var(--healthy)',
            }}>
              {formatProb(p.failure_probability)}
            </span>
            <span style={{ fontSize: 11, color: 'var(--text-muted)', minWidth: 80, textAlign: 'right' }}>
              {timeAgo(p.predicted_at)}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
