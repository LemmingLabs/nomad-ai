export type UserRole = 'admin' | 'business' | 'user'

export type AuthUser = {
  id: number
  role: UserRole
  email?: string
  name?: string
}

export type LoginRequest = {
  email: string
  password: string
}

export type LoginResponse = {
  accessToken: string
  refreshToken?: string
  user?: AuthUser
}

export type RefreshResponse = {
  accessToken: string
  refreshToken?: string
}

export type AuthStatus = 'idle' | 'loading' | 'authenticated' | 'unauthenticated'

export type AuthState = {
  status: AuthStatus
  user: AuthUser | null
}
