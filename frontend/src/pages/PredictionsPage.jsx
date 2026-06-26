import React, { useCallback, useState } from 'react'
import PredictionsTable from '../components/predictions/PredictionsTable'
import ProbabilityChart from '../components/predictions/ProbabilityChart'
import Card from '../components/shared/Card'
import PageHeader from '../components/shared/PageHeader'
import { getPredictions } from '../api/client'
import { usePolling } from '../hooks/usePolling'

export default function PredictionsPage() {
  const [machineFilter, setMachineFilter] = useState('')

  const fetcher = useCallback(
    () => getPredictions({ limit: 100, ...(machineFilter ? { machine_id: machineFilter } : {}) }),
    [machineFilter]
  )
  const { data: predictions, loading } = usePolling(fetcher, 5000)

  return (
    <div className="animate-fade-in">
      <PageHeader
        title="Predictions"
        subtitle="LightGBM failure probability — streamed from the prediction engine"
        action={
          <input
            placeholder="Filter by machine ID…"
            value={machineFilter}
            onChange={e => setMachineFilter(e.target.value)}
            style={{ width: 200 }}
          />
        }
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: 16, marginBottom: 16 }}>
        <Card title="Probability Distribution" subtitle="Bucketed by risk band">
          <ProbabilityChart predictions={predictions} />
        </Card>
        <Card>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            {[
              { label: 'Total', value: predictions?.length ?? 0, color: 'var(--accent)' },
              { label: 'Failures', value: predictions?.filter(p => p.failure_prediction).length ?? 0, color: 'var(--critical)' },
              { label: 'High Risk >70%', value: predictions?.filter(p => p.failure_probability > 0.7).length ?? 0, color: 'var(--warning)' },
              { label: 'Healthy <50%', value: predictions?.filter(p => p.failure_probability <= 0.5).length ?? 0, color: 'var(--healthy)' },
            ].map(s => (
              <div key={s.label} style={{ background: 'var(--bg-elevated)', borderRadius: 8, padding: '14px 16px' }}>
                <div style={{ fontSize: 10, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', marginBottom: 4 }}>{s.label}</div>
                <div style={{ fontSize: 26, fontWeight: 700, color: s.color, lineHeight: 1 }}>{s.value}</div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card title="All Predictions" subtitle="Sorted by latest first" noPad>
        <PredictionsTable predictions={predictions} loading={loading} />
      </Card>
    </div>
  )
}
