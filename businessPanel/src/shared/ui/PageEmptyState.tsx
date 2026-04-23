import type { ReactNode } from 'react'

type PageEmptyStateProps = {
  title: string
  description?: string
  action?: ReactNode
}

export function PageEmptyState({ title, description, action }: PageEmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed border-neutral-300 bg-white p-6">
      <h2 className="text-base font-semibold">{title}</h2>
      {description ? <p className="mt-1 text-sm text-neutral-600">{description}</p> : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  )
}

