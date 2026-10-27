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
    <div className="dashboard-shell min-h-dvh">
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
            'dashboard-surface fixed inset-y-0 left-0 z-50 w-72 overflow-y-auto border-r shadow-xl transition-transform duration-200 md:static md:z-auto md:w-64 md:translate-x-0 md:shadow-none',
            isMobileNavOpen ? 'block translate-x-0' : 'hidden md:block md:translate-x-0',
          ].join(' ')}
        >
          <div className="px-4 py-4">
            <div className="text-base font-semibold">{title}</div>
            <div className="dashboard-muted text-xs">Role: {roleLabel}</div>
          </div>

          <nav aria-label="Dashboard navigation" className="px-2 py-2">
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setIsMobileNavOpen(false)}
                className={({ isActive }) =>
                  [
                    'dashboard-nav-link',
                    isActive ? 'font-medium' : '',
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
          <header className="dashboard-surface border-b">
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
                <div className="dashboard-muted truncate text-sm">{title}</div>
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
