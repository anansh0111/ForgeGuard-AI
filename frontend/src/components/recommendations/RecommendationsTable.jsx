import React from 'react'
import { SeverityBadge } from '../shared/Badge'
import { formatDateTime, timeAgo } from '../../utils/helpers'
import Spinner from '../shared/Spinner'

export default function RecommendationsTable({ recommendations, loading }) {
  if (loading) return <Spinner message="Loading recommendations…" />
  if (!recommendations?.length) return (
    <p style={{ color: 'var(--text-muted)', padding: 20, fontSize: 14 }}>No recommendations yet.</p>
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
      {recommendations.map(r => (
        <div key={r.id} style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--border)',
          display: 'grid',
          gridTemplateColumns: '90px 1fr auto',
          gap: 16,
          alignItems: 'start',
        }}>
          <div style={{ paddingTop: 2 }}>
            <SeverityBadge severity={r.severity} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent)' }}>
                {r.machine_id}
              </span>
              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
                {r.action}
              </span>
            </div>
            {r.details && (
              <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5, maxWidth: 600 }}>
                {r.details}
              </p>
            )}
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', whiteSpace: 'nowrap', textAlign: 'right', paddingTop: 2 }}>
            <div>{formatDateTime(r.created_at)}</div>
            <div style={{ marginTop: 2 }}>{timeAgo(r.created_at)}</div>
          </div>
        </div>
      ))}
    </div>
  )
}
