import { useNavigate } from 'react-router-dom'

import { useAuthStore } from '../../features/auth/model/auth.store'
import { DashboardShell } from './DashboardShell'

const businessNav = [
  { to: '/business', label: 'Dashboard' },
  { to: '/business/profile', label: 'Business Profile' },
  { to: '/business/media', label: 'Media Library' },
  { to: '/business/sponsored-places', label: 'Sponsored Places' },
  { to: '/business/analytics', label: 'Analytics' },
]

export function BusinessLayout() {
  const navigate = useNavigate()
  const role = useAuthStore((s) => s.user?.role ?? 'business')
  const logout = useAuthStore((s) => s.logout)

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <DashboardShell
      title="NomadAI Business Panel"
      roleLabel={role}
      nav={businessNav}
      onLogout={handleLogout}
    />
  )
}
