import { useEffect, useState, type ReactNode } from 'react'
import { NavLink, Outlet } from 'react-router-dom'

export type DashboardNavItem = {
  to: string
  label: string
}

type DashboardShellProps = {
  title: string
  roleLabel: string
  nav: DashboardNavItem[]
  onLogout: () => void
  children?: ReactNode
}

export function DashboardShell({
  title,
  roleLabel,
  nav,
  onLogout,
  children,
}: DashboardShellProps) {
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false)

  useEffect(() => {
    if (!isMobileNavOpen) return

    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setIsMobileNavOpen(false)
    }

    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [isMobileNavOpen])

  return (
    <div className="min-h-dvh bg-neutral-50 text-neutral-900">
      <div className="flex min-h-dvh">
        {isMobileNavOpen ? (
          <button
            type="button"
            aria-label="Close navigation menu"
            onClick={() => setIsMobileNavOpen(false)}
            className="fixed inset-0 z-40 bg-neutral-950/40 md:hidden"
          />
        ) : null}

        <aside
          id="dashboard-navigation"
          className={[
            'fixed inset-y-0 left-0 z-50 w-72 overflow-y-auto border-r border-neutral-200 bg-white shadow-xl transition-transform duration-200 md:static md:z-auto md:w-64 md:translate-x-0 md:shadow-none',
            isMobileNavOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
          ].join(' ')}
        >
          <div className="px-4 py-4">
            <div className="text-base font-semibold">{title}</div>
            <div className="text-xs text-neutral-500">Role: {roleLabel}</div>
          </div>

          <nav aria-label="Dashboard navigation" className="px-2 py-2">
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setIsMobileNavOpen(false)}
                className={({ isActive }) =>
                  [
                    'block rounded-md px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2',
                    isActive
                      ? 'bg-neutral-100 font-medium text-neutral-900'
                      : 'text-neutral-700 hover:bg-neutral-50',
                  ].join(' ')
                }
                end
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="border-b border-neutral-200 bg-white">
            <div className="flex items-center justify-between gap-3 px-4 py-3 sm:px-6 sm:py-4">
              <div className="flex min-w-0 items-center gap-3">
                <button
                  type="button"
                  aria-controls="dashboard-navigation"
                  aria-expanded={isMobileNavOpen}
                  aria-label={isMobileNavOpen ? 'Close navigation menu' : 'Open navigation menu'}
                  onClick={() => setIsMobileNavOpen((open) => !open)}
                  className="inline-flex size-10 shrink-0 items-center justify-center rounded-md border border-neutral-200 bg-white text-lg leading-none hover:bg-neutral-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2 md:hidden"
                >
                  <span aria-hidden="true">{isMobileNavOpen ? '×' : '☰'}</span>
                </button>
                <div className="truncate text-sm text-neutral-600">{title}</div>
              </div>
              <button
                type="button"
                onClick={onLogout}
                className="shrink-0 rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2"
              >
                Logout
              </button>
            </div>
          </header>

          <main className="min-w-0 flex-1 px-4 py-5 sm:px-6 sm:py-6">
            {children ?? <Outlet />}
          </main>
        </div>
      </div>
    </div>
  )
}
