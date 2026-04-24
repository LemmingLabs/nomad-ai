import { useNavigate } from 'react-router-dom'

import { SectionCard } from '../../shared/ui/SectionCard'

export function BusinessMediaPage() {
  const navigate = useNavigate()

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-lg font-semibold">Media library</h1>
        <p className="text-sm text-neutral-600">
          Media for sponsored content is now managed inside each sponsored place.
        </p>
      </header>

      <SectionCard title="Moved workflow">
        <div className="space-y-3">
          <p className="text-sm text-neutral-700">
            Image upload by URL is no longer the primary workflow for sponsored places.
            Open a sponsored place card to upload and manage its media with file upload.
          </p>

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => navigate('/business/sponsored-places')}
              className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800"
            >
              Open Sponsored Places
            </button>
            <button
              type="button"
              onClick={() => navigate('/business')}
              className="rounded-md border border-neutral-200 bg-white px-4 py-2 text-sm font-medium hover:bg-neutral-50"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </SectionCard>
    </div>
  )
}
