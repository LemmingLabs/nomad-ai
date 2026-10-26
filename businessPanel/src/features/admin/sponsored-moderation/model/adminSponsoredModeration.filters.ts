import type { AdminSponsoredPlaceListFilters } from './adminSponsoredModeration.types'

export function mapFiltersToQueryParams(filters: AdminSponsoredPlaceListFilters) {
  const presetParams = filters.preset === 'pending'
    ? { pending: true }
    : filters.preset === 'approved'
      ? { approved: true }
      : filters.preset === 'inactive'
        ? { active: false }
        : {}
  return {
    ...presetParams,
    ...(filters.country_code ? { country_code: filters.country_code } : {}),
  }
}

