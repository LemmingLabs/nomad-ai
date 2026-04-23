import { Navigate } from 'react-router-dom'

import { useAuthStore } from '../features/auth/model/auth.store'

export function HomeRedirectPage() {
  const role = useAuthStore((s) => s.user?.role)

  if (role === 'admin') return <Navigate to="/admin" replace />
  if (role === 'business') return <Navigate to="/business" replace />

  return <Navigate to="/login" replace />
}
