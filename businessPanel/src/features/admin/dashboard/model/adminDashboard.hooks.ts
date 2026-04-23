import { useMemo } from 'react'

import { useAdminBusinessesQuery } from '../../businesses/model/adminBusinesses.hooks'
import type { AdminBusiness } from '../../businesses/model/adminBusinesses.types'
import { useAdminSponsoredPlacesQuery } from '../../sponsored-moderation/model/adminSponsoredModeration.hooks'
import { useAdminSubscriptionPlansQuery } from '../../subscription-plans/model/adminSubscriptionPlans.hooks'
import { useAdminUsersQuery } from '../../users/model/adminUsers.hooks'
import type { AdminUser } from '../../users/model/adminUsers.types'

type RecentItem<T> = {
  item: T
  createdAt: string
  createdAtMs: number
}

function getRecentByCreatedAt<T extends { created_at?: string }>(items: T[], limit = 5) {
  const parsed = items
    .map((item): RecentItem<T> | null => {
      const createdAt = item.created_at
      if (!createdAt) return null
      const ms = new Date(createdAt).getTime()
      if (Number.isNaN(ms)) return null
      return { item, createdAt, createdAtMs: ms }
    })
    .filter((v): v is RecentItem<T> => v != null)
    .sort((a, b) => b.createdAtMs - a.createdAtMs)
    .slice(0, limit)

  return parsed.map((v) => v.item)
}

export function useAdminDashboardData() {
  const usersQuery = useAdminUsersQuery()
  const businessesQuery = useAdminBusinessesQuery()
  const sponsoredPlacesQuery = useAdminSponsoredPlacesQuery({ preset: 'all' })
  const subscriptionPlansQuery = useAdminSubscriptionPlansQuery()

  const isLoading =
    usersQuery.isLoading ||
    businessesQuery.isLoading ||
    sponsoredPlacesQuery.isLoading ||
    subscriptionPlansQuery.isLoading

  const isError =
    usersQuery.isError ||
    businessesQuery.isError ||
    sponsoredPlacesQuery.isError ||
    subscriptionPlansQuery.isError

  const error = usersQuery.isError
    ? usersQuery.error
    : businessesQuery.isError
      ? businessesQuery.error
      : sponsoredPlacesQuery.isError
        ? sponsoredPlacesQuery.error
        : subscriptionPlansQuery.isError
          ? subscriptionPlansQuery.error
          : null

  const counts = useMemo(() => {
    const users = usersQuery.data ?? []
    const businesses = businessesQuery.data ?? []
    const sponsoredPlaces = sponsoredPlacesQuery.data ?? []
    const subscriptionPlans = subscriptionPlansQuery.data ?? []

    const pendingModeration = sponsoredPlaces.filter((p) => !p.is_approved).length
    const activePlans = subscriptionPlans.filter((p) => p.is_active).length
    const inactivePlans = subscriptionPlans.filter((p) => !p.is_active).length

    return {
      usersCount: users.length,
      businessesCount: businesses.length,
      sponsoredPlacesCount: sponsoredPlaces.length,
      pendingModerationCount: pendingModeration,
      activeSubscriptionPlansCount: activePlans,
      inactiveSubscriptionPlansCount: inactivePlans,
    }
  }, [
    usersQuery.data,
    businessesQuery.data,
    sponsoredPlacesQuery.data,
    subscriptionPlansQuery.data,
  ])

  const recent = useMemo(() => {
    const users = (usersQuery.data ?? []) as AdminUser[]
    const businesses = (businessesQuery.data ?? []) as AdminBusiness[]

    return {
      recentUsers: getRecentByCreatedAt(users, 5),
      recentBusinesses: getRecentByCreatedAt(businesses, 5),
    }
  }, [usersQuery.data, businessesQuery.data])

  const refetchAll = () => {
    void usersQuery.refetch()
    void businessesQuery.refetch()
    void sponsoredPlacesQuery.refetch()
    void subscriptionPlansQuery.refetch()
  }

  return {
    isLoading,
    isError,
    error,
    refetchAll,
    counts,
    recent,
  }
}

