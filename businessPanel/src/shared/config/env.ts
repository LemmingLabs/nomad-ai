type ViteEnv = {
  VITE_API_BASE_URL?: string
  VITE_GOOGLE_MAPS_API_KEY?: string
  VITE_GOOGLE_MAPS_MAP_ID?: string
}

const viteEnv = import.meta.env as unknown as ViteEnv

export const env = {
  apiBaseUrl: viteEnv.VITE_API_BASE_URL ?? '/api/v1',
  googleMapsApiKey: viteEnv.VITE_GOOGLE_MAPS_API_KEY?.trim() ?? '',
  googleMapsMapId: viteEnv.VITE_GOOGLE_MAPS_MAP_ID?.trim() ?? '',
} as const
