type PageLoadingStateProps = {
  message?: string
}

export function PageLoadingState({ message = 'Loading...' }: PageLoadingStateProps) {
  return <div className="dashboard-muted text-sm" role="status" aria-live="polite">{message}</div>
}

