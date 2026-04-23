type AdminSponsoredModerationEmptyStateProps = {
  title?: string
  description?: string
}

export function AdminSponsoredModerationEmptyState({
  title = 'No sponsored places',
  description = 'Nothing matched the selected filter.',
}: AdminSponsoredModerationEmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed border-neutral-300 bg-white p-6">
      <h2 className="text-base font-semibold">{title}</h2>
      <p className="mt-1 text-sm text-neutral-600">{description}</p>
    </div>
  )
}

