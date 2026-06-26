import React, { useCallback } from 'react'
import StatCard from '../components/dashboard/StatCard'
import MachineTable from '../components/dashboard/MachineTable'
import RiskTrendChart from '../components/dashboard/RiskTrendChart'
import RecentPredictions from '../components/dashboard/RecentPredictions'
import Card from '../components/shared/Card'
import PageHeader from '../components/shared/PageHeader'
import { getMachineStats, getMachines, getPredictions } from '../api/client'
import { usePolling } from '../hooks/usePolling'
import { formatPct } from '../utils/helpers'

export default function DashboardPage() {
  const { data: stats } = usePolling(useCallback(() => getMachineStats(), []), 5000)
  const { data: machines, loading: loadingMachines } = usePolling(useCallback(() => getMachines(), []), 10000)
  const { data: predictions } = usePolling(useCallback(() => getPredictions({ limit: 50 }), []), 5000)

  return (
    <div className="animate-fade-in">
      <PageHeader
        title="Operations Dashboard"
        subtitle="Live fleet health — updates every 5 seconds"
      />

      {/* KPI Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        <StatCard
          label="Total Machines"
          value={stats?.total_machines ?? '—'}
          sub="Registered units"
          accent
          color="var(--accent)"
        />
        <StatCard
          label="Critical"
          value={stats?.critical_machines ?? '—'}
          sub="Immediate action needed"
          accent
          color="var(--critical)"
        />
        <StatCard
          label="Average Failure Risk"
          value={stats ? formatPct(stats.average_failure_risk) : '—'}
          sub="Across all predictions"
          accent
          color={
            stats?.average_failure_risk > 0.7 ? 'var(--critical)' :
            stats?.average_failure_risk > 0.5 ? 'var(--warning)' : 'var(--healthy)'
          }
        />
        <StatCard
          label="Predictions Today"
          value={stats?.total_predictions_today ?? '—'}
          sub="Since midnight UTC"
          accent
        />
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 24 }}>
        <Card title="Failure Risk Trend" subtitle="Last 40 predictions across all machines">
          <RiskTrendChart predictions={predictions} />
        </Card>
        <Card title="Recent Predictions" subtitle="Latest sensor cycle results">
          <RecentPredictions predictions={predictions} />
        </Card>
      </div>

      {/* Machine Fleet */}
      <Card title="Machine Fleet" subtitle={`${machines?.length ?? 0} units registered`} noPad>
        <MachineTable machines={machines} loading={loadingMachines} />
      </Card>
    </div>
  )
}
