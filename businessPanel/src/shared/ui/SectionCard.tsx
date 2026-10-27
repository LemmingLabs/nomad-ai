import type { ReactNode } from 'react'

type SectionCardProps = {
  title?: string
  description?: string
  actions?: ReactNode
  children: ReactNode
}

export function SectionCard({ title, description, actions, children }: SectionCardProps) {
  return (
    <section className="shared-section-card">
      {title || description || actions ? (
        <header className="mb-4 flex items-start justify-between gap-4">
          <div>
            {title ? <h2 className="text-base font-semibold">{title}</h2> : null}
            {description ? (
              <p className="shared-section-description mt-1 text-sm">{description}</p>
            ) : null}
          </div>
          {actions ? <div className="shrink-0">{actions}</div> : null}
        </header>
      ) : null}
      {children}
    </section>
  )
}

