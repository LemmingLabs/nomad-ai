import type { ReactNode } from 'react'
import { Navigate, Outlet } from 'react-router-dom'

import { useAuthStore } from '../model/auth.store'
import type { UserRole } from '../model/auth.types'

type RoleGuardProps = {
  allowedRoles: UserRole[]
  children?: ReactNode
}

export function RoleGuard({ allowedRoles, children }: RoleGuardProps) {
  const status = useAuthStore((s) => s.status)
  const user = useAuthStore((s) => s.user)

  if (status === 'idle' || status === 'loading') {
    return <div className="p-6 text-sm text-neutral-600">Loading...</div>
  }

  if (status === 'unauthenticated') {
    return <Navigate to="/login" replace />
  }

  if (!user || !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />
  }

  return children ? <>{children}</> : <Outlet />
}
