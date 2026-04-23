import type { ReactNode } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { useAuthStore } from '../model/auth.store'

type AuthGuardProps = {
  children?: ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const status = useAuthStore((s) => s.status)
  const location = useLocation()

  if (status === 'idle' || status === 'loading') {
    return <div className="p-6 text-sm text-neutral-600">Loading...</div>
  }

  if (status === 'unauthenticated') {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return children ? <>{children}</> : <Outlet />
}
