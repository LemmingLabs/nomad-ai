export const queryKeys = {
  auth: {
    me: ['auth', 'me'] as const,
  },
  admin: {
    users: {
      root: ['admin', 'users'] as const,
      list: ['admin', 'users', 'list'] as const,
      details: (userId: number) => ['admin', 'users', 'details', userId] as const,
    },
    subscriptionPlans: {
      root: ['admin', 'subscriptionPlans'] as const,
      list: ['admin', 'subscriptionPlans', 'list'] as const,
    },
    businesses: {
      list: ['admin', 'businesses', 'list'] as const,
      details: (businessId: number) =>
        ['admin', 'businesses', 'details', businessId] as const,
    },
    sponsoredModeration: {
      root: ['admin', 'sponsoredModeration'] as const,
      list: (preset: string) => ['admin', 'sponsoredModeration', 'list', preset] as const,
      details: (placeId: number) =>
        ['admin', 'sponsoredModeration', 'details', placeId] as const,
    },
    analytics: {
      root: ['admin', 'analytics'] as const,
      business: (businessId: number) => ['admin', 'analytics', 'business', businessId] as const,
      sponsoredPlace: (placeId: number) =>
        ['admin', 'analytics', 'sponsoredPlace', placeId] as const,
    },
  },
  business: {
    profile: ['business', 'profile'] as const,
    media: ['business', 'media'] as const,
    sponsoredPlaces: ['business', 'sponsoredPlaces'] as const,
    analytics: ['business', 'analytics'] as const,
    analyticsOverview: ['business', 'analytics', 'overview'] as const,
    sponsoredPlaceAnalytics: (placeId: number) =>
      ['business', 'analytics', 'sponsoredPlaces', placeId] as const,
  },
  analytics: {
    root: ['analytics'] as const,
  },
} as const
