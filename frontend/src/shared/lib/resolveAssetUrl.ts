import { config } from '../config';

function getBackendOrigin() {
  const fallbackOrigin =
    typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000';

  try {
    return new URL(config.apiBaseUrl, fallbackOrigin).origin;
  } catch {
    return fallbackOrigin;
  }
}

export function resolveAssetUrl(url?: string | null): string {
  if (!url) return '';

  if (/^https?:\/\//i.test(url)) {
    return url;
  }

  const normalizedPath = url.startsWith('/') ? url : `/${url}`;
  return `${getBackendOrigin()}${normalizedPath}`;
}
