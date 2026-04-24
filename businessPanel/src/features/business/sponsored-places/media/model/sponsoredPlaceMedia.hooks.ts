import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '../../../../../shared/api'
import { sponsoredPlaceMediaApi } from '../api/sponsoredPlaceMedia.api'
import type {
  DeleteSponsoredPlaceMediaPayload,
  UploadSponsoredPlaceMediaPayload,
} from './sponsoredPlaceMedia.types'

export function useSponsoredPlaceMediaQuery(
  placeId: number,
  enabled = true,
) {
  return useQuery({
    queryKey: queryKeys.business.sponsoredPlaceMedia(placeId),
    queryFn: () => sponsoredPlaceMediaApi.getSponsoredPlaceMedia(placeId),
    enabled: enabled && Number.isFinite(placeId) && placeId > 0,
  })
}

export function useUploadSponsoredPlaceMediaMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ placeId, file, type }: UploadSponsoredPlaceMediaPayload) =>
      sponsoredPlaceMediaApi.uploadSponsoredPlaceMedia(placeId, file, type),
    onSuccess: async (_data, variables) => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: queryKeys.business.sponsoredPlaceMedia(variables.placeId),
        }),
        queryClient.invalidateQueries({
          queryKey: queryKeys.business.sponsoredPlaces,
        }),
      ])
    },
  })
}

export function useDeleteSponsoredPlaceMediaMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ placeId, mediaId }: DeleteSponsoredPlaceMediaPayload) =>
      sponsoredPlaceMediaApi.deleteSponsoredPlaceMedia(placeId, mediaId),
    onSuccess: async (_data, variables) => {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: queryKeys.business.sponsoredPlaceMedia(variables.placeId),
        }),
        queryClient.invalidateQueries({
          queryKey: queryKeys.business.sponsoredPlaces,
        }),
      ])
    },
  })
}
