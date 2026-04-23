export type UserRole = 'user' | 'business' | 'admin'

export type AdminUser = {
  id: number
  email?: string
  name?: string
  role: UserRole
  is_active?: boolean
  created_at?: string
  updated_at?: string
}

export type AdminUserDetails = AdminUser & {
  // Backend may return additional fields later; keep extensible.
}

export type UpdateUserRolePayload = {
  role: UserRole
}

