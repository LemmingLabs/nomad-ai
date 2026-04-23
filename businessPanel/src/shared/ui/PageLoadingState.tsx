type PageLoadingStateProps = {
  message?: string
}

export function PageLoadingState({ message = 'Loading...' }: PageLoadingStateProps) {
  return <div className="text-sm text-neutral-600">{message}</div>
}

