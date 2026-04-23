import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '../../../../shared/api'
import { adminSubscriptionPlansApi } from '../api/adminSubscriptionPlans.api'
import type {
  CreateSubscriptionPlanPayload,
  UpdateSubscriptionPlanPayload,
} from './adminSubscriptionPlans.types'

export function useAdminSubscriptionPlansQuery() {
  return useQuery({
    queryKey: queryKeys.admin.subscriptionPlans.list,
    queryFn: () => adminSubscriptionPlansApi.getAdminSubscriptionPlans(),
  })
}

function useInvalidateSubscriptionPlans() {
  const queryClient = useQueryClient()
  return async () => {
    await queryClient.invalidateQueries({ queryKey: queryKeys.admin.subscriptionPlans.root })
  }
}

export function useCreateAdminSubscriptionPlanMutation() {
  const invalidate = useInvalidateSubscriptionPlans()
  return useMutation({
    mutationFn: (payload: CreateSubscriptionPlanPayload) =>
      adminSubscriptionPlansApi.createAdminSubscriptionPlan(payload),
    onSuccess: invalidate,
  })
}

export function useUpdateAdminSubscriptionPlanMutation() {
  const invalidate = useInvalidateSubscriptionPlans()
  return useMutation({
    mutationFn: ({ planId, payload }: { planId: number; payload: UpdateSubscriptionPlanPayload }) =>
      adminSubscriptionPlansApi.updateAdminSubscriptionPlan(planId, payload),
    onSuccess: invalidate,
  })
}

export function useActivateAdminSubscriptionPlanMutation() {
  const invalidate = useInvalidateSubscriptionPlans()
  return useMutation({
    mutationFn: (planId: number) => adminSubscriptionPlansApi.activateAdminSubscriptionPlan(planId),
    onSuccess: invalidate,
  })
}

export function useDeactivateAdminSubscriptionPlanMutation() {
  const invalidate = useInvalidateSubscriptionPlans()
  return useMutation({
    mutationFn: (planId: number) =>
      adminSubscriptionPlansApi.deactivateAdminSubscriptionPlan(planId),
    onSuccess: invalidate,
  })
}

