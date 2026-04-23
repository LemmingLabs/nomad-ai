import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '../../../../shared/api'
import { businessMediaApi } from '../api/businessMedia.api'
import type { CreateBusinessMediaPayload } from './businessMedia.types'

export function useBusinessMediaQuery() {
  return useQuery({
    queryKey: queryKeys.business.media,
    queryFn: () => businessMediaApi.getBusinessMedia(),
  })
}

export function useCreateBusinessMediaMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreateBusinessMediaPayload) =>
      businessMediaApi.createBusinessMedia(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.business.media })
    },
  })
}

export function useDeleteBusinessMediaMutation() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (mediaId: number) => businessMediaApi.deleteBusinessMedia(mediaId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.business.media })
    },
  })
}

