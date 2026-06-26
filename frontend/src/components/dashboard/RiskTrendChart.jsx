import React from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts'
import { formatDateTime } from '../../utils/helpers'

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div style={{
      background: 'var(--bg-elevated)', border: '1px solid var(--border-bright)',
      borderRadius: 8, padding: '8px 12px', fontSize: 12,
    }}>
      <div style={{ color: 'var(--text-muted)', marginBottom: 4 }}>{formatDateTime(d.predicted_at)}</div>
      <div style={{ color: 'var(--accent)', fontFamily: 'var(--font-mono)' }}>
        {(d.failure_probability * 100).toFixed(2)}% risk
      </div>
      <div style={{ color: 'var(--text-secondary)' }}>Machine: {d.machine_id}</div>
    </div>
  )
}

export default function RiskTrendChart({ predictions }) {
  if (!predictions?.length) return (
    <p style={{ color: 'var(--text-muted)', fontSize: 13, padding: '12px 0' }}>No prediction data yet.</p>
  )

  const data = [...predictions]
    .sort((a, b) => new Date(a.predicted_at) - new Date(b.predicted_at))
    .slice(-40)

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
        <XAxis dataKey="predicted_at" hide />
        <YAxis domain={[0, 1]} tickFormatter={v => `${(v*100).toFixed(0)}%`}
          tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
        <Tooltip content={<CustomTooltip />} />
        <ReferenceLine y={0.9} stroke="var(--critical)" strokeDasharray="4 4" strokeOpacity={0.6} />
        <ReferenceLine y={0.7} stroke="var(--warning)" strokeDasharray="4 4" strokeOpacity={0.5} />
        <ReferenceLine y={0.5} stroke="var(--inspection)" strokeDasharray="4 4" strokeOpacity={0.4} />
        <Line
          type="monotone" dataKey="failure_probability"
          stroke="var(--accent)" strokeWidth={2}
          dot={false} activeDot={{ r: 4, fill: 'var(--accent)' }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
