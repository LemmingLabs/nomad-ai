import { afterEach, expect, test, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { AdminDashboardView } from '../../src/features/admin/dashboard/ui/AdminDashboardView'
import { AdminDashboardPage } from '../../src/pages/admin/AdminDashboardPage'

const dashboard = vi.hoisted(() => ({ loading: false, failed: false, refetch: vi.fn() }))
vi.mock('../../src/features/admin/dashboard/model/adminDashboard.hooks', () => ({
  useAdminDashboardData: () => ({
    isLoading: dashboard.loading,
    isError: dashboard.failed,
    error: new Error('Dashboard unavailable'),
    refetchAll: dashboard.refetch,
    counts: { usersCount: 0, businessesCount: 0, sponsoredPlacesCount: 0, pendingModerationCount: 0, activeSubscriptionPlansCount: 0, inactiveSubscriptionPlansCount: 0 },
    recent: { recentUsers: [], recentBusinesses: [] },
  }),
}))

afterEach(() => {
  cleanup()
  dashboard.loading = false
  dashboard.failed = false
  dashboard.refetch.mockClear()
})

test('shows moderation workload and links to the review queue', async () => {
  render(
    <MemoryRouter initialEntries={['/admin']}>
      <Routes>
        <Route path="/admin" element={<AdminDashboardView
          counts={{
            usersCount: 12, businessesCount: 3, sponsoredPlacesCount: 6,
            pendingModerationCount: 2, activeSubscriptionPlansCount: 3,
            inactiveSubscriptionPlansCount: 1,
          }}
          recentUsers={[]}
          recentBusinesses={[]}
        />} />
        <Route path="/admin/sponsored-moderation" element={<p>Review queue</p>} />
      </Routes>
    </MemoryRouter>,
  )

  expect(screen.getByText('Pending sponsored places')).toBeTruthy()
  expect(screen.getByText('Inactive subscription plans')).toBeTruthy()
  await userEvent.setup().click(screen.getByRole('button', { name: 'Review' }))
  expect(await screen.findByText('Review queue')).toBeTruthy()
})

test('shows the dashboard error and retries its queries', async () => {
  dashboard.failed = true
  render(<MemoryRouter><AdminDashboardPage /></MemoryRouter>)
  expect(screen.getByText('Dashboard unavailable')).toBeTruthy()
  await userEvent.setup().click(screen.getByRole('button', { name: 'Retry' }))
  expect(dashboard.refetch).toHaveBeenCalledOnce()
})

test('shows a loading state before dashboard data is ready', () => {
  dashboard.loading = true
  render(<MemoryRouter><AdminDashboardPage /></MemoryRouter>)
  expect(screen.getByText('Loading dashboard...')).toBeTruthy()
})
