type AdminAnalyticsEmptyStateProps = {
  title?: string
  description?: string
}

export function AdminAnalyticsEmptyState({
  title = 'No items available',
  description = 'There is nothing to analyze yet.',
}: AdminAnalyticsEmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed border-neutral-300 bg-white p-6">
      <h2 className="text-base font-semibold">{title}</h2>
      <p className="mt-1 text-sm text-neutral-600">{description}</p>
    </div>
  )
}

