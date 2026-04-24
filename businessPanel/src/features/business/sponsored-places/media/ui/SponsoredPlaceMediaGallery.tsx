import type { SponsoredPlaceMedia } from '../model/sponsoredPlaceMedia.types'
import { resolveAssetUrl } from '../../../../../shared/lib/resolveAssetUrl'

type SponsoredPlaceMediaGalleryProps = {
  items: SponsoredPlaceMedia[]
  deletingMediaId?: number | null
  onDelete: (media: SponsoredPlaceMedia) => void
}

export function SponsoredPlaceMediaGallery({
  items,
  deletingMediaId,
  onDelete,
}: SponsoredPlaceMediaGalleryProps) {
  if (items.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-neutral-200 bg-neutral-50 px-3 py-4 text-sm text-neutral-500">
        No images yet
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      {items.slice(0, 6).map((item) => (
        <div
          key={item.id}
          className="overflow-hidden rounded-md border border-neutral-200 bg-white"
        >
          <div className="aspect-[4/3] bg-neutral-100">
            <img
              src={resolveAssetUrl(item.url)}
              alt={item.filename ?? `Sponsored place media ${item.id}`}
              className="h-full w-full object-cover"
              loading="lazy"
            />
          </div>

          <div className="flex items-center justify-between gap-2 p-2">
            <div className="min-w-0 text-xs text-neutral-500">
              <div className="truncate">{item.filename ?? 'Image'}</div>
            </div>

            <button
              type="button"
              onClick={() => onDelete(item)}
              disabled={deletingMediaId === item.id}
              className="shrink-0 rounded-md border border-neutral-200 px-2 py-1 text-xs font-medium text-red-700 hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {deletingMediaId === item.id ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
