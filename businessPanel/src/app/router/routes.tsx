import type { RouteObject } from 'react-router-dom'

import { AppLayout } from '../layouts/AppLayout'
import { AdminLayout } from '../layouts/AdminLayout'
import { BusinessLayout } from '../layouts/BusinessLayout'
import { HomeRedirectPage } from '../../pages/HomeRedirectPage'
import { LoginPage } from '../../pages/LoginPage'
import { NotFoundPage } from '../../pages/NotFoundPage'
import { AuthGuard } from '../../features/auth/guards/AuthGuard'
import { RoleGuard } from '../../features/auth/guards/RoleGuard'
import { AdminAnalyticsPage } from '../../pages/admin/AdminAnalyticsPage'
import { AdminBusinessesPage } from '../../pages/admin/AdminBusinessesPage'
import { AdminDashboardPage } from '../../pages/admin/AdminDashboardPage'
import { AdminModerationPage } from '../../pages/admin/AdminModerationPage'
import { AdminUsersPage } from '../../pages/admin/AdminUsersPage'
import { BusinessAnalyticsPage } from '../../pages/business/BusinessAnalyticsPage'
import { BusinessDashboardPage } from '../../pages/business/BusinessDashboardPage'
import { BusinessMediaPage } from '../../pages/business/BusinessMediaPage'
import { BusinessProfilePage } from '../../pages/business/BusinessProfilePage'
import { BusinessSponsoredPlacesPage } from '../../pages/business/BusinessSponsoredPlacesPage'

export const routes: RouteObject[] = [
  {
    element: <AppLayout />,
    children: [
      { path: 'login', element: <LoginPage /> },
      {
        element: <AuthGuard />,
        children: [
          { index: true, element: <HomeRedirectPage /> },
          {
            path: 'admin',
            element: (
              <RoleGuard allowedRoles={['admin']}>
                <AdminLayout />
              </RoleGuard>
            ),
            children: [
              { index: true, element: <AdminDashboardPage /> },
              { path: 'users', element: <AdminUsersPage /> },
              { path: 'businesses', element: <AdminBusinessesPage /> },
              {
                path: 'sponsored-moderation',
                element: <AdminModerationPage />,
              },
              { path: 'analytics', element: <AdminAnalyticsPage /> },
            ],
          },
          {
            path: 'business',
            element: (
              <RoleGuard allowedRoles={['business']}>
                <BusinessLayout />
              </RoleGuard>
            ),
            children: [
              { index: true, element: <BusinessDashboardPage /> },
              { path: 'profile', element: <BusinessProfilePage /> },
              { path: 'media', element: <BusinessMediaPage /> },
              {
                path: 'sponsored-places',
                element: <BusinessSponsoredPlacesPage />,
              },
              { path: 'analytics', element: <BusinessAnalyticsPage /> },
            ],
          },
        ],
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]
