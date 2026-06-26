import React from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'

const COLORS = {
  critical:   '#ef4444',
  warning:    '#f59e0b',
  inspection: '#8b5cf6',
  healthy:    '#10b981',
}

export default function SeverityBreakdown({ recommendations }) {
  if (!recommendations?.length) return null

  const counts = recommendations.reduce((acc, r) => {
    acc[r.severity] = (acc[r.severity] || 0) + 1
    return acc
  }, {})

  const data = Object.entries(counts).map(([name, value]) => ({ name, value }))

  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie data={data} dataKey="value" cx="50%" cy="50%" outerRadius={70} innerRadius={40}>
          {data.map((d, i) => (
            <Cell key={i} fill={COLORS[d.name] || '#3b82f6'} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-bright)', borderRadius: 8, fontSize: 12 }}
          formatter={(v, n) => [v, n.charAt(0).toUpperCase() + n.slice(1)]}
        />
        <Legend
          formatter={(v) => <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{v.charAt(0).toUpperCase() + v.slice(1)}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
