import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '../../../../shared/api'
import { sponsoredPlacesApi } from '../api/sponsoredPlaces.api'
import type {
  CreateSponsoredPlacePayload,
  SponsoredPlace,
  SponsoredPlaceFormValues,
  UpdateSponsoredPlacePayload,
  EnabledDestination,
} from './sponsoredPlaces.types'
import { apiClient } from '../../../../shared/api/client'

function emptyToNull(value: string): string | null {
  const trimmed = value.trim()
  return trimmed === '' ? null : trimmed
}

export function mapSponsoredPlaceToFormValues(
  place: SponsoredPlace,
): SponsoredPlaceFormValues {
  return {
    title: place.title ?? '',
    description: place.description ?? '',
    country_code: place.country_code ?? 'KG',
    region: place.region ?? '',
    operating_language: place.operating_language ?? 'en',
    city: place.city ?? '',
    category: place.category ?? '',
    address: place.address ?? '',
    lat: String(place.lat ?? ''),
    lng: String(place.lng ?? ''),
    contact_phone: place.contact_phone ?? '',
    website_url: place.website_url ?? '',
    cta_text: place.cta_text ?? '',
  }
}

export function mapFormValuesToCreatePayload(
  values: SponsoredPlaceFormValues,
): CreateSponsoredPlacePayload {
  return {
    title: values.title.trim(),
    description: values.description.trim(),
    country_code: values.country_code,
    region: emptyToNull(values.region),
    operating_language: values.operating_language,
    city: values.city.trim(),
    category: values.category.trim(),
    address: values.address.trim(),
    lat: Number(values.lat),
    lng: Number(values.lng),
    contact_phone: emptyToNull(values.contact_phone),
    website_url: emptyToNull(values.website_url),
    cta_text: emptyToNull(values.cta_text),
  }
}

export function mapFormValuesToUpdatePayload(
  values: SponsoredPlaceFormValues,
): UpdateSponsoredPlacePayload {
  return mapFormValuesToCreatePayload(values)
}

export function useSponsoredPlacesQuery() {
  return useQuery({
    queryKey: queryKeys.business.sponsoredPlaces,
    queryFn: () => sponsoredPlacesApi.getSponsoredPlaces(),
  })
}

export function useEnabledDestinationsQuery() {
  return useQuery({
    queryKey: ['destinations', 'enabled'],
    queryFn: async () => {
      const { data } = await apiClient.get<EnabledDestination[]>('/partner-markets')
      return data
    },
  })
}

export function useCreateSponsoredPlaceMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreateSponsoredPlacePayload) =>
      sponsoredPlacesApi.createSponsoredPlace(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.business.sponsoredPlaces,
      })
    },
  })
}

export function useUpdateSponsoredPlaceMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (vars: { id: number; payload: UpdateSponsoredPlacePayload }) =>
      sponsoredPlacesApi.updateSponsoredPlace(vars.id, vars.payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.business.sponsoredPlaces,
      })
    },
  })
}

export function useDeleteSponsoredPlaceMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => sponsoredPlacesApi.deleteSponsoredPlace(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.business.sponsoredPlaces,
      })
    },
  })
}

