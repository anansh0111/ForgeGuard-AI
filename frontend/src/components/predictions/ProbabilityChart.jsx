import React from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const BINS = [
  { label: '0–10%',  min: 0,   max: 0.1,  color: '#10b981' },
  { label: '10–30%', min: 0.1, max: 0.3,  color: '#10b981' },
  { label: '30–50%', min: 0.3, max: 0.5,  color: '#3b82f6' },
  { label: '50–70%', min: 0.5, max: 0.7,  color: '#8b5cf6' },
  { label: '70–90%', min: 0.7, max: 0.9,  color: '#f59e0b' },
  { label: '90–100%',min: 0.9, max: 1.01, color: '#ef4444' },
]

export default function ProbabilityChart({ predictions }) {
  if (!predictions?.length) return null

  const data = BINS.map(b => ({
    label: b.label,
    count: predictions.filter(p => p.failure_probability >= b.min && p.failure_probability < b.max).length,
    color: b.color,
  }))

  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data} margin={{ top: 4, right: 8, left: -24, bottom: 0 }}>
        <XAxis dataKey="label" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
        <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} allowDecimals={false} />
        <Tooltip
          contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-bright)', borderRadius: 8, fontSize: 12 }}
          labelStyle={{ color: 'var(--text-primary)' }}
          itemStyle={{ color: 'var(--text-secondary)' }}
          formatter={(v) => [v, 'Predictions']}
        />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((d, i) => <Cell key={i} fill={d.color} fillOpacity={0.85} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
