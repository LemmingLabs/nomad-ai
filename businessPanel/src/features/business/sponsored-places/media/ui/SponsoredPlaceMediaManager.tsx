import { useMemo, useState } from 'react'

import { confirmAction } from '../../../../../shared/lib/confirm'
import { getErrorMessage } from '../../../../../shared/lib/getErrorMessage'
import {
  useDeleteSponsoredPlaceMediaMutation,
  useSponsoredPlaceMediaQuery,
  useUploadSponsoredPlaceMediaMutation,
} from '../model/sponsoredPlaceMedia.hooks'
import type { SponsoredPlaceMedia } from '../model/sponsoredPlaceMedia.types'
import { SponsoredPlaceMediaGallery } from './SponsoredPlaceMediaGallery'
import { SponsoredPlaceMediaUpload } from './SponsoredPlaceMediaUpload'

type SponsoredPlaceMediaManagerProps = {
  placeId: number
  initialItems?: SponsoredPlaceMedia[]
}

export function SponsoredPlaceMediaManager({
  placeId,
  initialItems = [],
}: SponsoredPlaceMediaManagerProps) {
  const mediaQuery = useSponsoredPlaceMediaQuery(placeId)
  const uploadMutation = useUploadSponsoredPlaceMediaMutation()
  const deleteMutation = useDeleteSponsoredPlaceMediaMutation()
  const [deletingMediaId, setDeletingMediaId] = useState<number | null>(null)

  const items = useMemo(
    () => mediaQuery.data ?? initialItems,
    [initialItems, mediaQuery.data],
  )

  const handleUpload = async (file: File) => {
    await uploadMutation.mutateAsync({ placeId, file, type: 'image' })
  }

  const handleDelete = async (media: SponsoredPlaceMedia) => {
    const ok = confirmAction({
      title: 'Delete this image?',
      description: 'This media item will be removed from the sponsored place.',
    })
    if (!ok) return

    setDeletingMediaId(media.id)
    try {
      await deleteMutation.mutateAsync({ placeId, mediaId: media.id })
    } finally {
      setDeletingMediaId(null)
    }
  }

  return (
    <section className="mt-4 space-y-3 rounded-lg border border-neutral-200 bg-neutral-50 p-3">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h4 className="text-sm font-semibold text-neutral-900">Media gallery</h4>
          <p className="text-xs text-neutral-500">
            Upload images for this sponsored place only.
          </p>
        </div>

        <SponsoredPlaceMediaUpload
          onUpload={handleUpload}
          isUploading={uploadMutation.isPending}
          disabled={mediaQuery.isLoading}
        />
      </div>

      <SponsoredPlaceMediaGallery
        items={items}
        deletingMediaId={deletingMediaId}
        onDelete={handleDelete}
      />

      {mediaQuery.isError ? (
        <p className="text-sm text-red-600">
          {getErrorMessage(
            mediaQuery.error,
            'Failed to load sponsored place images.',
          )}
        </p>
      ) : null}

      {uploadMutation.isError ? (
        <p className="text-sm text-red-600">
          {getErrorMessage(
            uploadMutation.error,
            'Failed to upload image. Please try again.',
          )}
        </p>
      ) : null}

      {deleteMutation.isError ? (
        <p className="text-sm text-red-600">
          {getErrorMessage(
            deleteMutation.error,
            'Failed to delete image. Please try again.',
          )}
        </p>
      ) : null}
    </section>
  )
}
