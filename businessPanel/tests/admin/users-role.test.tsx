import { afterEach, expect, test, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AdminUsersPage } from '../../src/pages/admin/AdminUsersPage'
import { adminUsersApi } from '../../src/features/admin/users/api/adminUsers.api'
import { useAuthStore } from '../../src/features/auth/model/auth.store'

vi.mock('../../src/features/admin/users/api/adminUsers.api', () => ({
  adminUsersApi: { getAdminUsers: vi.fn(), getAdminUserDetails: vi.fn(), updateAdminUserRole: vi.fn() },
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
  useAuthStore.setState({ status: 'unauthenticated', user: null })
})

test('protects the current admin role and lets them promote another user', async () => {
  useAuthStore.setState({ status: 'authenticated', user: { id: 1, role: 'admin' } })
  const users = [
    { id: 1, email: 'admin@example.com', role: 'admin' as const },
    { id: 2, email: 'guide@example.com', role: 'user' as const },
  ]
  vi.mocked(adminUsersApi.getAdminUsers).mockResolvedValue(users)
  vi.mocked(adminUsersApi.getAdminUserDetails).mockImplementation(async (id) => users.find((entry) => entry.id === id)!)
  vi.mocked(adminUsersApi.updateAdminUserRole).mockResolvedValue({ id: 2, role: 'business' })
  const user = userEvent.setup()

  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <AdminUsersPage />
    </QueryClientProvider>,
  )

  expect(await screen.findByText('You cannot change your own role.')).toBeTruthy()
  await user.click(screen.getAllByRole('button', { name: 'View details' })[1])
  await screen.findByRole('button', { name: 'Update role' })
  await user.selectOptions(screen.getByRole('combobox', { name: 'Role' }), 'business')
  await user.click(screen.getByRole('button', { name: 'Update role' }))
  await waitFor(() => expect(adminUsersApi.updateAdminUserRole).toHaveBeenCalledWith(2, { role: 'business' }))
})
