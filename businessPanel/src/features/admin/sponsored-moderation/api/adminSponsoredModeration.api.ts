import { apiClient } from '../../../../shared/api/client'
import type {
  AdminSponsoredPlace,
  AdminSponsoredPlaceDetails,
  AdminSponsoredPlaceListFilters,
} from '../model/adminSponsoredModeration.types'
import { mapFiltersToQueryParams } from '../model/adminSponsoredModeration.filters'

export const adminSponsoredModerationApi = {
  async getAdminSponsoredPlaces(filters?: AdminSponsoredPlaceListFilters) {
    const params = filters ? mapFiltersToQueryParams(filters) : undefined
    const { data } = await apiClient.get<AdminSponsoredPlace[]>(
      '/admin/sponsored-places',
      { params },
    )
    return data
  },

  async getAdminSponsoredPlaceDetails(placeId: number) {
    const { data } = await apiClient.get<AdminSponsoredPlaceDetails>(
      `/admin/sponsored-places/${placeId}`,
    )
    return data
  },

  async approveAdminSponsoredPlace(placeId: number) {
    const { data } = await apiClient.patch<AdminSponsoredPlaceDetails>(
      `/admin/sponsored-places/${placeId}/approve`,
    )
    return data
  },

  async rejectAdminSponsoredPlace(placeId: number) {
    const { data } = await apiClient.patch<AdminSponsoredPlaceDetails>(
      `/admin/sponsored-places/${placeId}/reject`,
    )
    return data
  },

  async activateAdminSponsoredPlace(placeId: number) {
    const { data } = await apiClient.patch<AdminSponsoredPlaceDetails>(
      `/admin/sponsored-places/${placeId}/activate`,
    )
    return data
  },

  async deactivateAdminSponsoredPlace(placeId: number) {
    const { data } = await apiClient.patch<AdminSponsoredPlaceDetails>(
      `/admin/sponsored-places/${placeId}/deactivate`,
    )
    return data
  },
}

