import React from 'react'
import { NavLink } from 'react-router-dom'
import styles from './Sidebar.module.css'

const NAV = [
  { to: '/',               icon: '⬡', label: 'Dashboard'       },
  { to: '/predictions',    icon: '◈', label: 'Predictions'     },
  { to: '/recommendations',icon: '◎', label: 'Recommendations' },
]

export default function Sidebar() {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>
        <span className={styles.brandIcon}>⬡</span>
        <div>
          <div className={styles.brandName}>ForgeGuard</div>
          <div className={styles.brandSub}>AI Platform</div>
        </div>
      </div>

      <nav className={styles.nav}>
        {NAV.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `${styles.navItem} ${isActive ? styles.active : ''}`
            }
          >
            <span className={styles.navIcon}>{icon}</span>
            <span className={styles.navLabel}>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className={styles.footer}>
        <div className={styles.footerBadge}>
          <span className={styles.liveDot} />
          Live Monitoring
        </div>
        <div className={styles.footerCredit}>by Anansh</div>
      </div>
    </aside>
  )
}
