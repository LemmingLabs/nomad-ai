import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '../../../../shared/api'
import { adminSponsoredModerationApi } from '../api/adminSponsoredModeration.api'
import type { AdminSponsoredPlaceListFilters } from './adminSponsoredModeration.types'

export function useAdminSponsoredPlacesQuery(filters: AdminSponsoredPlaceListFilters) {
  return useQuery({
    queryKey: queryKeys.admin.sponsoredModeration.list(filters.preset),
    queryFn: () => adminSponsoredModerationApi.getAdminSponsoredPlaces(filters),
  })
}

export function useAdminSponsoredPlaceDetailsQuery(placeId: number, enabled = true) {
  return useQuery({
    queryKey: queryKeys.admin.sponsoredModeration.details(placeId),
    queryFn: () => adminSponsoredModerationApi.getAdminSponsoredPlaceDetails(placeId),
    enabled: enabled && Number.isFinite(placeId),
  })
}

function useInvalidateModerationQueries() {
  const queryClient = useQueryClient()
  return async () => {
    await queryClient.invalidateQueries({
      queryKey: queryKeys.admin.sponsoredModeration.root,
    })
  }
}

export function useApproveSponsoredPlaceMutation() {
  const invalidate = useInvalidateModerationQueries()
  return useMutation({
    mutationFn: (placeId: number) =>
      adminSponsoredModerationApi.approveAdminSponsoredPlace(placeId),
    onSuccess: invalidate,
  })
}

export function useRejectSponsoredPlaceMutation() {
  const invalidate = useInvalidateModerationQueries()
  return useMutation({
    mutationFn: (placeId: number) =>
      adminSponsoredModerationApi.rejectAdminSponsoredPlace(placeId),
    onSuccess: invalidate,
  })
}

export function useActivateSponsoredPlaceMutation() {
  const invalidate = useInvalidateModerationQueries()
  return useMutation({
    mutationFn: (placeId: number) =>
      adminSponsoredModerationApi.activateAdminSponsoredPlace(placeId),
    onSuccess: invalidate,
  })
}

export function useDeactivateSponsoredPlaceMutation() {
  const invalidate = useInvalidateModerationQueries()
  return useMutation({
    mutationFn: (placeId: number) =>
      adminSponsoredModerationApi.deactivateAdminSponsoredPlace(placeId),
    onSuccess: invalidate,
  })
}

