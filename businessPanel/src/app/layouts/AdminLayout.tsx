import { useNavigate } from 'react-router-dom'

import { useAuthStore } from '../../features/auth/model/auth.store'
import { DashboardShell } from './DashboardShell'

const adminNav = [
  { to: '/admin', label: 'Dashboard' },
  { to: '/admin/businesses', label: 'Businesses' },
  { to: '/admin/sponsored-moderation', label: 'Sponsored Moderation' },
  { to: '/admin/analytics', label: 'Analytics' },
]

export function AdminLayout() {
  const navigate = useNavigate()
  const role = useAuthStore((s) => s.user?.role ?? 'admin')
  const logout = useAuthStore((s) => s.logout)

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <DashboardShell
      title="NomadAI Business Panel"
      roleLabel={role}
      nav={adminNav}
      onLogout={handleLogout}
    />
  )
}
