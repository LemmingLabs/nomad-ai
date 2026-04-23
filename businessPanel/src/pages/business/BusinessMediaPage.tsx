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
import { confirmAction } from '../../shared/lib/confirm'
import { getErrorMessage } from '../../shared/lib/getErrorMessage'
import { PageErrorState } from '../../shared/ui/PageErrorState'
import { PageLoadingState } from '../../shared/ui/PageLoadingState'
import { SectionCard } from '../../shared/ui/SectionCard'

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
    const ok = confirmAction({
      title: 'Delete this media item?',
      description: 'This action cannot be undone.',
    })
    if (!ok) return

    setDeletingId(id)
    try {
      await deleteMutation.mutateAsync(id)
    } finally {
      setDeletingId(null)
    }
  }

  if (mediaQuery.isLoading) {
    return <PageLoadingState message="Loading media..." />
  }

  if (mediaQuery.isError) {
    return (
      <PageErrorState
        title="Media library"
        message={getErrorMessage(mediaQuery.error, 'Failed to load media')}
        onRetry={() => mediaQuery.refetch()}
      />
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

      <SectionCard title="Add media">
        <BusinessMediaForm isSubmitting={isSubmitting} onSubmit={handleAdd} />
        {createMutation.isError ? (
          <p className="mt-4 text-sm text-red-600">
            {getErrorMessage(createMutation.error, 'Failed to add media. Please try again.')}
          </p>
        ) : null}
      </SectionCard>

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
