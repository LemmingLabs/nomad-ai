import { useMemo, useState } from 'react'

import {
  mapFormValuesToCreatePayload,
  mapFormValuesToUpdatePayload,
  mapSponsoredPlaceToFormValues,
  useCreateSponsoredPlaceMutation,
  useDeleteSponsoredPlaceMutation,
  useSponsoredPlacesQuery,
  useUpdateSponsoredPlaceMutation,
} from '../../features/business/sponsored-places/model/sponsoredPlaces.hooks'
import type {
  SponsoredPlace,
  SponsoredPlaceFormValues,
} from '../../features/business/sponsored-places/model/sponsoredPlaces.types'
import { SponsoredPlaceForm } from '../../features/business/sponsored-places/ui/SponsoredPlaceForm'
import { SponsoredPlacesEmptyState } from '../../features/business/sponsored-places/ui/SponsoredPlacesEmptyState'
import { SponsoredPlacesList } from '../../features/business/sponsored-places/ui/SponsoredPlacesList'
import { confirmAction } from '../../shared/lib/confirm'
import { getErrorMessage } from '../../shared/lib/getErrorMessage'
import { PageErrorState } from '../../shared/ui/PageErrorState'
import { PageLoadingState } from '../../shared/ui/PageLoadingState'
import { SectionCard } from '../../shared/ui/SectionCard'

const emptyFormValues: SponsoredPlaceFormValues = {
  title: '',
  description: '',
  city: '',
  category: '',
  address: '',
  lat: '',
  lng: '',
  contact_phone: '',
  website_url: '',
  cta_text: '',
}

export function BusinessSponsoredPlacesPage() {
  const placesQuery = useSponsoredPlacesQuery()
  const createMutation = useCreateSponsoredPlaceMutation()
  const updateMutation = useUpdateSponsoredPlaceMutation()
  const deleteMutation = useDeleteSponsoredPlaceMutation()

  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editing, setEditing] = useState<SponsoredPlace | null>(null)
  const [deactivatingId, setDeactivatingId] = useState<number | null>(null)

  const initialValues = useMemo(() => {
    if (!editing) return emptyFormValues
    return mapSponsoredPlaceToFormValues(editing)
  }, [editing])

  const isSubmitting = createMutation.isPending || updateMutation.isPending

  const openCreate = () => {
    setEditing(null)
    setIsFormOpen(true)
  }

  const openEdit = (place: SponsoredPlace) => {
    setEditing(place)
    setIsFormOpen(true)
  }

  const closeForm = () => {
    setIsFormOpen(false)
    setEditing(null)
  }

  const handleSubmit = async (values: SponsoredPlaceFormValues) => {
    if (editing) {
      await updateMutation.mutateAsync({
        id: editing.id,
        payload: mapFormValuesToUpdatePayload(values),
      })
      closeForm()
      return
    }

    await createMutation.mutateAsync(mapFormValuesToCreatePayload(values))
    closeForm()
  }

  const handleDeactivate = async (id: number) => {
    const ok = confirmAction({
      title: 'Deactivate this sponsored place?',
      description: 'You can activate it again later.',
    })
    if (!ok) return

    setDeactivatingId(id)
    try {
      await deleteMutation.mutateAsync(id)
    } finally {
      setDeactivatingId(null)
    }
  }

  if (placesQuery.isLoading) {
    return <PageLoadingState message="Loading sponsored places..." />
  }

  if (placesQuery.isError) {
    return (
      <PageErrorState
        title="Sponsored places"
        message={getErrorMessage(placesQuery.error, 'Failed to load sponsored places')}
        onRetry={() => placesQuery.refetch()}
      />
    )
  }

  const places = placesQuery.data ?? []

  return (
    <div className="space-y-6">
      <header className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-lg font-semibold">Sponsored places</h1>
          <p className="text-sm text-neutral-600">
            Create and manage your sponsored places. Deactivate to stop showing it.
          </p>
        </div>

        <button
          type="button"
          onClick={openCreate}
          className="shrink-0 rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800"
        >
          Create
        </button>
      </header>

      {places.length === 0 && !isFormOpen ? (
        <SponsoredPlacesEmptyState onCreate={openCreate} />
      ) : null}

      {isFormOpen ? (
        <SectionCard
          title={editing ? 'Edit sponsored place' : 'Create sponsored place'}
        >
          <SponsoredPlaceForm
            initialValues={initialValues}
            submitLabel={editing ? 'Save changes' : 'Create'}
            isSubmitting={isSubmitting}
            onCancel={closeForm}
            onSubmit={handleSubmit}
          />

          {createMutation.isError || updateMutation.isError ? (
            <p className="mt-4 text-sm text-red-600">
              {getErrorMessage(
                (createMutation.error ?? updateMutation.error) as unknown,
                'Failed to save sponsored place. Please try again.',
              )}
            </p>
          ) : null}
        </SectionCard>
      ) : null}

      {places.length > 0 ? (
        <SponsoredPlacesList
          places={places}
          onEdit={openEdit}
          onDeactivate={handleDeactivate}
          deactivatingId={deactivatingId}
        />
      ) : null}

      {deleteMutation.isError ? (
        <p className="text-sm text-red-600">
          {getErrorMessage(
            deleteMutation.error,
            'Failed to deactivate sponsored place. Please try again.',
          )}
        </p>
      ) : null}
    </div>
  )
}
