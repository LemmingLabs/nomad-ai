import type { ReactNode } from 'react'

type BusinessProfileCardProps = {
  title: string
  description?: string
  children: ReactNode
}

export function BusinessProfileCard({
  title,
  description,
  children,
}: BusinessProfileCardProps) {
  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-6">
      <header className="mb-4">
        <h1 className="text-lg font-semibold">{title}</h1>
        {description ? (
          <p className="mt-1 text-sm text-neutral-600">{description}</p>
        ) : null}
      </header>
      {children}
    </section>
  )
}

