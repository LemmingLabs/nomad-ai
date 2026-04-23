import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">404 - Page not found</h1>
      <Link className="text-sm font-medium underline" to="/">
        Go to dashboard
      </Link>
    </div>
  )
}
