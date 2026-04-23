import { SectionCard } from './SectionCard'

type PageErrorStateProps = {
  title: string
  message: string
  onRetry?: () => void
  retryLabel?: string
}

export function PageErrorState({
  title,
  message,
  onRetry,
  retryLabel = 'Retry',
}: PageErrorStateProps) {
  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">{title}</h1>
      <SectionCard>
        <p className="text-sm text-neutral-700">{message}</p>
        {onRetry ? (
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
          >
            {retryLabel}
          </button>
        ) : null}
      </SectionCard>
    </div>
  )
}

