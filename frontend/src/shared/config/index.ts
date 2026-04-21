function normalizeApiBaseUrl(rawUrl: string): string {
  const trimmedUrl = rawUrl.trim().replace(/\/+$/, '');
  return trimmedUrl.endsWith('/api/v1') ? trimmedUrl : `${trimmedUrl}/api/v1`;
}

export const config = {
  apiBaseUrl: normalizeApiBaseUrl(
    typeof import.meta.env.VITE_API_BASE_URL === 'string'
      ? import.meta.env.VITE_API_BASE_URL
      : 'http://localhost:8000',
  ),
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
  storageKeys: {
    accessToken: 'access_token',
    guestTripId: 'guest_trip_id',
  },
} as const;
