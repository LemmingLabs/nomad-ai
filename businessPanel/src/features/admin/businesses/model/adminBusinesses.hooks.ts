import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '../../../../shared/api'
import { adminBusinessesApi } from '../api/adminBusinesses.api'

export function useAdminBusinessesQuery() {
  return useQuery({
    queryKey: queryKeys.admin.businesses.list,
    queryFn: () => adminBusinessesApi.getAdminBusinesses(),
  })
}

export function useAdminBusinessDetailsQuery(businessId: number, enabled = true) {
  return useQuery({
    queryKey: queryKeys.admin.businesses.details(businessId),
    queryFn: () => adminBusinessesApi.getAdminBusinessDetails(businessId),
    enabled: enabled && Number.isFinite(businessId),
  })
}

