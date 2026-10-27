import type { ReactNode } from 'react'

type StatusBadgeVariant = 'success' | 'warning' | 'neutral'

type StatusBadgeProps = {
  variant: StatusBadgeVariant
  children: ReactNode
  className?: string
}

function variantClass(variant: StatusBadgeVariant) {
  const base = 'shared-status-badge'
  if (variant === 'success') return `${base} shared-status-success`
  if (variant === 'warning') return `${base} shared-status-warning`
  return `${base} shared-status-neutral`
}

export function StatusBadge({ variant, children, className }: StatusBadgeProps) {
  return <span className={[variantClass(variant), className].filter(Boolean).join(' ')}>{children}</span>
}

