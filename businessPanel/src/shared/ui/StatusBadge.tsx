import type { ReactNode } from 'react'

type StatusBadgeVariant = 'success' | 'warning' | 'neutral'

type StatusBadgeProps = {
  variant: StatusBadgeVariant
  children: ReactNode
  className?: string
}

function variantClass(variant: StatusBadgeVariant) {
  const base =
    'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset'
  if (variant === 'success') return `${base} bg-green-50 text-green-700 ring-green-600/20`
  if (variant === 'warning') return `${base} bg-amber-50 text-amber-700 ring-amber-600/20`
  return `${base} bg-neutral-50 text-neutral-700 ring-neutral-600/20`
}

export function StatusBadge({ variant, children, className }: StatusBadgeProps) {
  return <span className={[variantClass(variant), className].filter(Boolean).join(' ')}>{children}</span>
}

