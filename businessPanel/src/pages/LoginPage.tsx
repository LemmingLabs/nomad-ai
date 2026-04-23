import { useMemo, useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'

import { LoginForm } from '../features/auth/ui/LoginForm'
import { useAuthStore } from '../features/auth/model/auth.store'
import type { UserRole } from '../features/auth/model/auth.types'
import { getErrorMessage } from '../shared/lib/getErrorMessage'
import { PageLoadingState } from '../shared/ui/PageLoadingState'
import { SectionCard } from '../shared/ui/SectionCard'

type LoginLocationState = {
  from?: { pathname?: string }
}

function roleHomePath(role: UserRole | undefined) {
  if (role === 'admin') return '/admin'
  if (role === 'business') return '/business'
  return '/'
}

function isAllowedReturnPath(role: UserRole, path: string) {
  if (role === 'admin') return path.startsWith('/admin')
  if (role === 'business') return path.startsWith('/business')
  return false
}

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()

  const status = useAuthStore((s) => s.status)
  const user = useAuthStore((s) => s.user)
  const login = useAuthStore((s) => s.login)

  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const returnPath = useMemo(() => {
    const state = location.state as LoginLocationState | null
    const fromPath = state?.from?.pathname
    if (!fromPath) return null
    if (fromPath === '/login') return null
    return fromPath
  }, [location.state])

  if (status === 'idle' || (status === 'loading' && !isSubmitting)) {
    return (
      <div className="mx-auto max-w-md p-6">
        <PageLoadingState message="Loading..." />
      </div>
    )
  }

  if (status === 'authenticated' && user?.role) {
    return <Navigate to={roleHomePath(user.role)} replace />
  }

  return (
    <div className="min-h-[calc(100dvh-4rem)] px-6 py-10">
      <div className="mx-auto w-full max-w-md space-y-6">
        <header className="space-y-1">
          <h1 className="text-2xl font-semibold">Sign in</h1>
          <p className="text-sm text-neutral-600">NomadAI Business Panel</p>
        </header>

        <SectionCard>
          <LoginForm
            isSubmitting={isSubmitting}
            errorMessage={errorMessage}
            onSubmit={async (values) => {
              setErrorMessage(null)
              setIsSubmitting(true)
              try {
                await login(values)
                const role = useAuthStore.getState().user?.role
                const fallback = roleHomePath(role)
                const next =
                  role && returnPath && isAllowedReturnPath(role, returnPath)
                    ? returnPath
                    : fallback
                navigate(next, { replace: true })
              } catch (err) {
                setErrorMessage(getErrorMessage(err, 'Invalid email or password'))
              } finally {
                setIsSubmitting(false)
              }
            }}
          />
        </SectionCard>
      </div>
    </div>
  )
}
