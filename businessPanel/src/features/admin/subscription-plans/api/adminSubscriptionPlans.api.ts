import { apiClient } from '../../../../shared/api'
import type {
  CreateSubscriptionPlanPayload,
  SubscriptionPlan,
  UpdateSubscriptionPlanPayload,
} from '../model/adminSubscriptionPlans.types'

export const adminSubscriptionPlansApi = {
  async getAdminSubscriptionPlans() {
    const { data } = await apiClient.get<SubscriptionPlan[]>('/admin/subscription-plans')
    return data
  },

  async createAdminSubscriptionPlan(payload: CreateSubscriptionPlanPayload) {
    const { data } = await apiClient.post<SubscriptionPlan>(
      '/admin/subscription-plans',
      payload,
    )
    return data
  },

  async updateAdminSubscriptionPlan(planId: number, payload: UpdateSubscriptionPlanPayload) {
    const { data } = await apiClient.patch<SubscriptionPlan>(
      `/admin/subscription-plans/${planId}`,
      payload,
    )
    return data
  },

  async activateAdminSubscriptionPlan(planId: number) {
    const { data } = await apiClient.patch<SubscriptionPlan>(
      `/admin/subscription-plans/${planId}/activate`,
    )
    return data
  },

  async deactivateAdminSubscriptionPlan(planId: number) {
    const { data } = await apiClient.patch<SubscriptionPlan>(
      `/admin/subscription-plans/${planId}/deactivate`,
    )
    return data
  },
}

