import type { AdminSponsoredPlaceListFilters } from './adminSponsoredModeration.types'

export function mapFiltersToQueryParams(filters: AdminSponsoredPlaceListFilters) {
  if (filters.preset === 'pending') return { pending: true }
  if (filters.preset === 'approved') return { approved: true }
  if (filters.preset === 'inactive') return { active: false }
  return {}
}

