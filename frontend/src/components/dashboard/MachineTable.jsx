import React from 'react'
import { StatusBadge } from '../shared/Badge'
import Spinner from '../shared/Spinner'

export default function MachineTable({ machines, loading }) {
  if (loading) return <Spinner message="Loading machines…" />
  if (!machines?.length) return (
    <p style={{ color: 'var(--text-muted)', padding: 20, fontSize: 14 }}>No machines registered.</p>
  )

  return (
    <div style={{ overflowX: 'auto' }}>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Type</th>
            <th>Location</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {machines.map(m => (
            <tr key={m.machine_id}>
              <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent)' }}>{m.machine_id}</td>
              <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{m.name}</td>
              <td>{m.machine_type}</td>
              <td>{m.location || '—'}</td>
              <td><StatusBadge status={m.status} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
