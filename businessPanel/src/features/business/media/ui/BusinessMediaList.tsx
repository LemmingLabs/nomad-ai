import type { BusinessMedia } from '../model/businessMedia.types'
import { BusinessMediaCard } from './BusinessMediaCard'

type BusinessMediaListProps = {
  items: BusinessMedia[]
  onDelete: (id: number) => void
  deletingId?: number | null
}

export function BusinessMediaList({ items, onDelete, deletingId }: BusinessMediaListProps) {
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      {items.map((item) => (
        <BusinessMediaCard
          key={item.id}
          item={item}
          onDelete={onDelete}
          isDeleting={deletingId === item.id}
        />
      ))}
    </div>
  )
}

