type ViteEnv = {
  VITE_API_BASE_URL?: string
}

const viteEnv = import.meta.env as unknown as ViteEnv

export const env = {
  apiBaseUrl: viteEnv.VITE_API_BASE_URL ?? '/api/v1',
} as const

