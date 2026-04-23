import type { BusinessMedia } from '../model/businessMedia.types'
import { formatDateTime } from '../../../../shared/lib/formatDateTime'

function formatMediaTypeLabel(type: BusinessMedia['type']) {
  if (type === 'logo') return 'Logo'
  return 'Image'
}

type BusinessMediaCardProps = {
  item: BusinessMedia
  onDelete: (id: number) => void
  isDeleting?: boolean
}

export function BusinessMediaCard({ item, onDelete, isDeleting }: BusinessMediaCardProps) {
  const createdAt = item.created_at ? formatDateTime(item.created_at) : null

  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="text-sm font-medium text-neutral-900">
            {formatMediaTypeLabel(item.type)}
          </div>
          <a
            href={item.url}
            target="_blank"
            rel="noreferrer"
            className="mt-1 block truncate text-sm text-neutral-700 underline"
            title={item.url}
          >
            {item.url}
          </a>
          {createdAt ? (
            <div className="mt-1 text-xs text-neutral-500">Added: {createdAt}</div>
          ) : null}
        </div>

        <button
          type="button"
          onClick={() => onDelete(item.id)}
          disabled={isDeleting}
          className="shrink-0 rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Delete
        </button>
      </div>
    </div>
  )
}
