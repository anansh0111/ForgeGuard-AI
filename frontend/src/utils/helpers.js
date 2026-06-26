import { format, formatDistanceToNow } from 'date-fns'

export const formatPct = (val) => `${(val * 100).toFixed(1)}%`
export const formatProb = (val) => (val * 100).toFixed(2) + '%'

export const timeAgo = (iso) => {
  try { return formatDistanceToNow(new Date(iso), { addSuffix: true }) }
  catch { return '—' }
}

export const formatDateTime = (iso) => {
  try { return format(new Date(iso), 'MMM d, HH:mm:ss') }
  catch { return '—' }
}

export const SEVERITY_META = {
  critical:   { label: 'Critical',   color: 'var(--critical)',   bg: 'var(--critical-dim)',   dot: '#ef4444' },
  warning:    { label: 'Warning',    color: 'var(--warning)',    bg: 'var(--warning-dim)',    dot: '#f59e0b' },
  inspection: { label: 'Inspection', color: 'var(--inspection)', bg: 'var(--inspection-dim)', dot: '#8b5cf6' },
  healthy:    { label: 'Healthy',    color: 'var(--healthy)',    bg: 'var(--healthy-dim)',    dot: '#10b981' },
}

export const STATUS_META = {
  critical:    { label: 'Critical',    color: 'var(--critical)',  bg: 'var(--critical-dim)'  },
  warning:     { label: 'Warning',     color: 'var(--warning)',   bg: 'var(--warning-dim)'   },
  operational: { label: 'Operational', color: 'var(--healthy)',   bg: 'var(--healthy-dim)'   },
  offline:     { label: 'Offline',     color: 'var(--text-muted)',bg: 'rgba(255,255,255,0.05)'},
}

export const clsx = (...args) => args.filter(Boolean).join(' ')
