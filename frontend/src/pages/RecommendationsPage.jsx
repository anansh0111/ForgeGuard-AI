import React, { useCallback, useState } from 'react'
import RecommendationsTable from '../components/recommendations/RecommendationsTable'
import SeverityBreakdown from '../components/recommendations/SeverityBreakdown'
import Card from '../components/shared/Card'
import PageHeader from '../components/shared/PageHeader'
import { getRecommendations } from '../api/client'
import { usePolling } from '../hooks/usePolling'

const SEVERITY_FILTERS = ['all', 'critical', 'warning', 'inspection', 'healthy']

export default function RecommendationsPage() {
  const [severityFilter, setSeverityFilter] = useState('all')

  const fetcher = useCallback(
    () => getRecommendations({ limit: 100, ...(severityFilter !== 'all' ? { severity: severityFilter } : {}) }),
    [severityFilter]
  )
  const { data: recommendations, loading } = usePolling(fetcher, 6000)

  return (
    <div className="animate-fade-in">
      <PageHeader
        title="Recommendations"
        subtitle="Rule-based maintenance actions from the recommendation engine"
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: 16, marginBottom: 16 }}>
        <div>
          {/* Filter tabs */}
          <div style={{ display: 'flex', gap: 6, marginBottom: 16 }}>
            {SEVERITY_FILTERS.map(f => (
              <button
                key={f}
                onClick={() => setSeverityFilter(f)}
                style={{
                  padding: '6px 14px', borderRadius: 20, fontSize: 12, fontWeight: 500,
                  background: severityFilter === f ? 'var(--accent-dim)' : 'var(--bg-card)',
                  color: severityFilter === f ? 'var(--accent)' : 'var(--text-secondary)',
                  border: `1px solid ${severityFilter === f ? 'rgba(59,130,246,0.3)' : 'var(--border)'}`,
                  transition: 'all 0.15s',
                }}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>

          <Card title="Action Log" noPad>
            <RecommendationsTable recommendations={recommendations} loading={loading} />
          </Card>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Card title="By Severity">
            <SeverityBreakdown recommendations={recommendations} />
          </Card>

          <Card>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {[
                { label: 'Critical', key: 'critical', color: 'var(--critical)', bg: 'var(--critical-dim)' },
                { label: 'Warning',  key: 'warning',  color: 'var(--warning)',  bg: 'var(--warning-dim)'  },
                { label: 'Inspection', key: 'inspection', color: 'var(--inspection)', bg: 'var(--inspection-dim)' },
                { label: 'Healthy', key: 'healthy', color: 'var(--healthy)', bg: 'var(--healthy-dim)' },
              ].map(s => {
                const count = recommendations?.filter(r => r.severity === s.key).length ?? 0
                return (
                  <div key={s.key} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '10px 14px', borderRadius: 8, background: s.bg,
                  }}>
                    <span style={{ fontSize: 13, color: s.color, fontWeight: 500 }}>{s.label}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 18, fontWeight: 700, color: s.color }}>{count}</span>
                  </div>
                )
              })}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
