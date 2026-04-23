import type { ReactNode } from 'react'
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
  return (
    <div className="min-h-dvh bg-neutral-50 text-neutral-900">
      <div className="flex min-h-dvh">
        <aside className="w-64 border-r border-neutral-200 bg-white">
          <div className="px-4 py-4">
            <div className="text-base font-semibold">{title}</div>
            <div className="text-xs text-neutral-500">Role: {roleLabel}</div>
          </div>

          <nav className="px-2 py-2">
            {nav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  [
                    'block rounded-md px-3 py-2 text-sm',
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
            <div className="flex items-center justify-between px-6 py-4">
              <div className="text-sm text-neutral-600">{title}</div>
              <button
                type="button"
                onClick={onLogout}
                className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
              >
                Logout
              </button>
            </div>
          </header>

          <main className="flex-1 px-6 py-6">
            {children ?? <Outlet />}
          </main>
        </div>
      </div>
    </div>
  )
}
