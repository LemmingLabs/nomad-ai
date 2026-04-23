import axios from 'axios'
import { useMemo } from 'react'

import {
  mapBusinessProfileToFormValues,
  mapFormValuesToUpsertPayload,
  useBusinessProfileQuery,
  useCreateBusinessProfileMutation,
  useUpdateBusinessProfileMutation,
} from '../../features/business/profile/model/businessProfile.hooks'
import type { BusinessProfileFormValues } from '../../features/business/profile/model/businessProfile.types'
import { BusinessProfileCard } from '../../features/business/profile/ui/BusinessProfileCard'
import { BusinessProfileEmptyState } from '../../features/business/profile/ui/BusinessProfileEmptyState'
import { BusinessProfileForm } from '../../features/business/profile/ui/BusinessProfileForm'

const emptyFormValues: BusinessProfileFormValues = {
  name: '',
  description: '',
  contact_phone: '',
  website_url: '',
}

export function BusinessProfilePage() {
  const profileQuery = useBusinessProfileQuery()
  const createMutation = useCreateBusinessProfileMutation()
  const updateMutation = useUpdateBusinessProfileMutation()

  const initialValues = useMemo(() => {
    if (!profileQuery.data) return emptyFormValues
    return mapBusinessProfileToFormValues(profileQuery.data)
  }, [profileQuery.data])

  const isSubmitting = createMutation.isPending || updateMutation.isPending

  const handleSubmit = async (values: BusinessProfileFormValues) => {
    const payload = mapFormValuesToUpsertPayload(values)

    if (profileQuery.data) {
      await updateMutation.mutateAsync(payload)
      return
    }

    await createMutation.mutateAsync(payload)
  }

  if (profileQuery.isLoading) {
    return <div className="text-sm text-neutral-600">Loading profile...</div>
  }

  if (profileQuery.isError) {
    const message = axios.isAxiosError(profileQuery.error)
      ? profileQuery.error.message
      : 'Failed to load profile'

    return (
      <div className="space-y-4">
        <h1 className="text-lg font-semibold">Business profile</h1>
        <div className="rounded-lg border border-neutral-200 bg-white p-6">
          <p className="text-sm text-neutral-700">{message}</p>
          <button
            type="button"
            onClick={() => profileQuery.refetch()}
            className="mt-4 rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  const hasProfile = profileQuery.data != null

  return (
    <div className="space-y-6">
      {!hasProfile ? <BusinessProfileEmptyState /> : null}

      <BusinessProfileCard
        title="Business profile"
        description={
          hasProfile
            ? 'Update your business details.'
            : 'Create your business profile to get started.'
        }
      >
        <BusinessProfileForm
          initialValues={initialValues}
          submitLabel={hasProfile ? 'Save changes' : 'Create profile'}
          isSubmitting={isSubmitting}
          onSubmit={handleSubmit}
        />

        {createMutation.isError || updateMutation.isError ? (
          <p className="mt-4 text-sm text-red-600">
            Failed to save profile. Please try again.
          </p>
        ) : null}
      </BusinessProfileCard>
    </div>
  )
}
