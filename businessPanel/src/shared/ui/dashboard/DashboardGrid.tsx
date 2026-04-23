import type { ReactNode } from 'react'

type DashboardGridProps = {
  children: ReactNode
  className?: string
}

export function DashboardGrid({ children, className }: DashboardGridProps) {
  return <div className={['grid gap-4', className].filter(Boolean).join(' ')}>{children}</div>
}

