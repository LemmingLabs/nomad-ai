export const queryKeys = {
  auth: {
    me: ['auth', 'me'] as const,
  },
  admin: {
    businesses: ['admin', 'businesses'] as const,
    sponsoredModeration: ['admin', 'sponsoredModeration'] as const,
    analytics: ['admin', 'analytics'] as const,
  },
  business: {
    profile: ['business', 'profile'] as const,
    media: ['business', 'media'] as const,
    sponsoredPlaces: ['business', 'sponsoredPlaces'] as const,
    analytics: ['business', 'analytics'] as const,
  },
  analytics: {
    root: ['analytics'] as const,
  },
} as const

