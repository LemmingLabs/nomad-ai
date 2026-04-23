type BusinessProfileEmptyStateProps = {
  onCreate?: () => void
  showCreateButton?: boolean
}

export function BusinessProfileEmptyState({
  onCreate,
  showCreateButton = false,
}: BusinessProfileEmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed border-neutral-300 bg-white p-6">
      <h2 className="text-base font-semibold">Business profile is not created yet</h2>
      <p className="mt-1 text-sm text-neutral-600">
        Create a profile to manage your business details.
      </p>

      {showCreateButton ? (
        <button
          type="button"
          onClick={onCreate}
          className="mt-4 rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
        >
          Create profile
        </button>
      ) : null}
    </div>
  )
}

