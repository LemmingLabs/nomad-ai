import type { RouteObject } from 'react-router-dom'

import { AppLayout } from '../layouts/AppLayout'
import { DashboardPage } from '../../pages/DashboardPage'
import { LoginPage } from '../../pages/LoginPage'
import { NotFoundPage } from '../../pages/NotFoundPage'
import { AuthGuard } from '../../features/auth/guards/AuthGuard'
import { RoleGuard } from '../../features/auth/guards/RoleGuard'

export const routes: RouteObject[] = [
  {
    element: <AppLayout />,
    children: [
      { path: 'login', element: <LoginPage /> },
      {
        element: <AuthGuard />,
        children: [
          { index: true, element: <DashboardPage /> },
          {
            element: <RoleGuard allowedRoles={['admin']} />,
            children: [{ path: 'admin', element: <DashboardPage /> }],
          },
        ],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]
