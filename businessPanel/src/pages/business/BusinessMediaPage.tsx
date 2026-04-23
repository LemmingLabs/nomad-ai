import axios from 'axios'
import { useState } from 'react'

import {
  useBusinessMediaQuery,
  useCreateBusinessMediaMutation,
  useDeleteBusinessMediaMutation,
} from '../../features/business/media/model/businessMedia.hooks'
import type { BusinessMediaFormValues } from '../../features/business/media/model/businessMedia.types'
import { BusinessMediaEmptyState } from '../../features/business/media/ui/BusinessMediaEmptyState'
import { BusinessMediaForm } from '../../features/business/media/ui/BusinessMediaForm'
import { BusinessMediaList } from '../../features/business/media/ui/BusinessMediaList'

export function BusinessMediaPage() {
  const mediaQuery = useBusinessMediaQuery()
  const createMutation = useCreateBusinessMediaMutation()
  const deleteMutation = useDeleteBusinessMediaMutation()
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const isSubmitting = createMutation.isPending

  const handleAdd = async (values: BusinessMediaFormValues) => {
    await createMutation.mutateAsync(values)
  }

  const handleDelete = async (id: number) => {
    const ok = window.confirm('Delete this media item?')
    if (!ok) return

    setDeletingId(id)
    try {
      await deleteMutation.mutateAsync(id)
    } finally {
      setDeletingId(null)
    }
  }

  if (mediaQuery.isLoading) {
    return <div className="text-sm text-neutral-600">Loading media...</div>
  }

  if (mediaQuery.isError) {
    const message = axios.isAxiosError(mediaQuery.error)
      ? mediaQuery.error.message
      : 'Failed to load media'

    return (
      <div className="space-y-4">
        <h1 className="text-lg font-semibold">Media library</h1>
        <div className="rounded-lg border border-neutral-200 bg-white p-6">
          <p className="text-sm text-neutral-700">{message}</p>
          <button
            type="button"
            onClick={() => mediaQuery.refetch()}
            className="mt-4 rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  const items = mediaQuery.data ?? []

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-lg font-semibold">Media library</h1>
        <p className="text-sm text-neutral-600">
          Add media items by URL. You can delete items anytime.
        </p>
      </header>

      <section className="rounded-lg border border-neutral-200 bg-white p-6">
        <h2 className="text-base font-semibold">Add media</h2>
        <div className="mt-4">
          <BusinessMediaForm isSubmitting={isSubmitting} onSubmit={handleAdd} />
        </div>

        {createMutation.isError ? (
          <p className="mt-4 text-sm text-red-600">
            Failed to add media. Please try again.
          </p>
        ) : null}
      </section>

      {items.length === 0 ? (
        <BusinessMediaEmptyState />
      ) : (
        <BusinessMediaList
          items={items}
          onDelete={handleDelete}
          deletingId={deletingId}
        />
      )}
    </div>
  )
}
