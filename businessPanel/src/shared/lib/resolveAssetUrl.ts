import { env } from '../config/env'

function getBackendOrigin() {
  const fallbackOrigin =
    typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000'

  try {
    return new URL(env.apiBaseUrl, fallbackOrigin).origin
  } catch {
    return fallbackOrigin
  }
}

export function resolveAssetUrl(url?: string | null) {
  if (!url) return ''

  if (/^https?:\/\//i.test(url)) {
    return url
  }

  const normalizedPath = url.startsWith('/') ? url : `/${url}`
  return `${getBackendOrigin()}${normalizedPath}`
}
