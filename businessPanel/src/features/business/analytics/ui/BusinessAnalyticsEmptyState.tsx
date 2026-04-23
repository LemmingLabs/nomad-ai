import { Link } from 'react-router-dom'

export function BusinessAnalyticsEmptyState() {
  return (
    <div className="rounded-lg border border-dashed border-neutral-300 bg-white p-6">
      <h2 className="text-base font-semibold">No sponsored places yet</h2>
      <p className="mt-1 text-sm text-neutral-600">
        Create a sponsored place to start tracking analytics.
      </p>
      <Link
        to="/business/sponsored-places"
        className="mt-4 inline-flex rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800"
      >
        Go to sponsored places
      </Link>
    </div>
  )
}

