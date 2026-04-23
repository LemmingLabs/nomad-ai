import { Outlet } from 'react-router-dom'

export function AppLayout() {
  return (
    <div className="min-h-dvh">
      <header className="border-b border-neutral-200 bg-white">
        <div className="mx-auto max-w-6xl px-6 py-4">
          <div className="text-base font-semibold">NomadAI Business Panel</div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}
