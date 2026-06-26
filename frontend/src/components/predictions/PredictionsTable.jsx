import React from 'react'
import { SeverityBadge } from '../shared/Badge'
import { formatProb, formatDateTime } from '../../utils/helpers'
import Spinner from '../shared/Spinner'

function getSeverity(prob) {
  if (prob > 0.9) return 'critical'
  if (prob > 0.7) return 'warning'
  if (prob > 0.5) return 'inspection'
  return 'healthy'
}

export default function PredictionsTable({ predictions, loading }) {
  if (loading) return <Spinner message="Loading predictions…" />
  if (!predictions?.length) return (
    <p style={{ color: 'var(--text-muted)', padding: 20, fontSize: 14 }}>No predictions found.</p>
  )

  return (
    <div style={{ overflowX: 'auto' }}>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Machine</th>
            <th>Risk Level</th>
            <th>Probability</th>
            <th>Prediction</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {predictions.map(p => (
            <tr key={p.id}>
              <td style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: 11 }}>#{p.id}</td>
              <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent)' }}>{p.machine_id}</td>
              <td><SeverityBadge severity={getSeverity(p.failure_probability)} /></td>
              <td>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{
                    width: 80, height: 6, background: 'var(--border)', borderRadius: 3, overflow: 'hidden',
                  }}>
                    <div style={{
                      height: '100%', borderRadius: 3,
                      width: `${p.failure_probability * 100}%`,
                      background: p.failure_probability > 0.7 ? 'var(--critical)' : p.failure_probability > 0.5 ? 'var(--warning)' : 'var(--healthy)',
                    }} />
                  </div>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-primary)' }}>
                    {formatProb(p.failure_probability)}
                  </span>
                </div>
              </td>
              <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                <span style={{ color: p.failure_prediction ? 'var(--critical)' : 'var(--healthy)' }}>
                  {p.failure_prediction ? 'FAIL' : 'OK'}
                </span>
              </td>
              <td style={{ fontSize: 12, color: 'var(--text-muted)' }}>{formatDateTime(p.predicted_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
