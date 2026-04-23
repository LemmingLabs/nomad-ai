type SponsoredPlacesEmptyStateProps = {
  onCreate: () => void
}

export function SponsoredPlacesEmptyState({ onCreate }: SponsoredPlacesEmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed border-neutral-300 bg-white p-6">
      <h2 className="text-base font-semibold">No sponsored places yet</h2>
      <p className="mt-1 text-sm text-neutral-600">
        Create a sponsored place to start running ads.
      </p>
      <button
        type="button"
        onClick={onCreate}
        className="mt-4 rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800"
      >
        Create
      </button>
    </div>
  )
}

