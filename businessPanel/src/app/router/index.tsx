import { RouterProvider, createBrowserRouter } from 'react-router-dom'

import { routes } from './routes'

const router = createBrowserRouter(routes)

export function AppRouter() {
  return <RouterProvider router={router} />
}
