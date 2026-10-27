import type { ReactNode } from 'react'

type PageEmptyStateProps = {
  title: string
  description?: string
  action?: ReactNode
}

export function PageEmptyState({ title, description, action }: PageEmptyStateProps) {
  return (
    <div className="shared-empty-state">
      <h2 className="text-base font-semibold">{title}</h2>
      {description ? <p className="shared-state-description mt-1 text-sm">{description}</p> : null}
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  )
}

