import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '../../../../shared/api'
import { businessProfileApi } from '../api/businessProfile.api'
import type {
  BusinessProfile,
  BusinessProfileFormValues,
  BusinessProfileUpsertPayload,
} from './businessProfile.types'

export function mapBusinessProfileToFormValues(
  profile: BusinessProfile,
): BusinessProfileFormValues {
  return {
    name: profile.name ?? '',
    description: profile.description ?? '',
    contact_phone: profile.contact_phone ?? '',
    website_url: profile.website_url ?? '',
  }
}

export function mapFormValuesToUpsertPayload(
  values: BusinessProfileFormValues,
): BusinessProfileUpsertPayload {
  const trimmedName = values.name.trim()
  const trimmedDescription = values.description.trim()
  const trimmedPhone = values.contact_phone.trim()
  const trimmedWebsite = values.website_url.trim()

  return {
    name: trimmedName,
    description: trimmedDescription === '' ? null : trimmedDescription,
    contact_phone: trimmedPhone === '' ? null : trimmedPhone,
    website_url: trimmedWebsite === '' ? null : trimmedWebsite,
  }
}

export function useBusinessProfileQuery() {
  return useQuery({
    queryKey: queryKeys.business.profile,
    queryFn: () => businessProfileApi.getBusinessProfile(),
  })
}

export function useCreateBusinessProfileMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: BusinessProfileUpsertPayload) =>
      businessProfileApi.createBusinessProfile(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.business.profile })
    },
  })
}

export function useUpdateBusinessProfileMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: Partial<BusinessProfileUpsertPayload>) =>
      businessProfileApi.updateBusinessProfile(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.business.profile })
    },
  })
}

