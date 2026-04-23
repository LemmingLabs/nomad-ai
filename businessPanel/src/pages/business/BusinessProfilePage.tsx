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
import { getErrorMessage } from '../../shared/lib/getErrorMessage'
import { PageErrorState } from '../../shared/ui/PageErrorState'
import { PageLoadingState } from '../../shared/ui/PageLoadingState'

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
    return <PageLoadingState message="Loading profile..." />
  }

  if (profileQuery.isError) {
    return (
      <PageErrorState
        title="Business profile"
        message={getErrorMessage(profileQuery.error, 'Failed to load profile')}
        onRetry={() => profileQuery.refetch()}
      />
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
            {getErrorMessage(
              (createMutation.error ?? updateMutation.error) as unknown,
              'Failed to save profile. Please try again.',
            )}
          </p>
        ) : null}
      </BusinessProfileCard>
    </div>
  )
}
