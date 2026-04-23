const ACCESS_TOKEN_KEY = 'nomadai.auth.accessToken'
const REFRESH_TOKEN_KEY = 'nomadai.auth.refreshToken'

function safeGetItem(key: string) {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

function safeSetItem(key: string, value: string) {
  try {
    localStorage.setItem(key, value)
  } catch {
    // ignore (e.g. storage disabled)
  }
}

function safeRemoveItem(key: string) {
  try {
    localStorage.removeItem(key)
  } catch {
    // ignore
  }
}

export const authStorage = {
  getAccessToken(): string | null {
    return safeGetItem(ACCESS_TOKEN_KEY)
  },

  getRefreshToken(): string | null {
    return safeGetItem(REFRESH_TOKEN_KEY)
  },

  setAccessToken(token: string) {
    safeSetItem(ACCESS_TOKEN_KEY, token)
  },

  setRefreshToken(token: string) {
    safeSetItem(REFRESH_TOKEN_KEY, token)
  },

  setTokens(tokens: { accessToken: string; refreshToken: string }) {
    this.setAccessToken(tokens.accessToken)
    this.setRefreshToken(tokens.refreshToken)
  },

  setTokensOptional(tokens: { accessToken: string; refreshToken?: string }) {
    this.setAccessToken(tokens.accessToken)
    if (tokens.refreshToken) {
      this.setRefreshToken(tokens.refreshToken)
    }
  },

  clearTokens() {
    safeRemoveItem(ACCESS_TOKEN_KEY)
    safeRemoveItem(REFRESH_TOKEN_KEY)
  },
}
