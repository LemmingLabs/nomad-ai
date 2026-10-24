import { afterEach, expect, test, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AdminSubscriptionPlansPage } from '../../src/pages/admin/AdminSubscriptionPlansPage'
import { adminSubscriptionPlansApi } from '../../src/features/admin/subscription-plans/api/adminSubscriptionPlans.api'

vi.mock('../../src/features/admin/subscription-plans/api/adminSubscriptionPlans.api', () => ({
  adminSubscriptionPlansApi: {
    getAdminSubscriptionPlans: vi.fn(),
    createAdminSubscriptionPlan: vi.fn(),
    updateAdminSubscriptionPlan: vi.fn(),
    activateAdminSubscriptionPlan: vi.fn(),
    deactivateAdminSubscriptionPlan: vi.fn(),
  },
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

test('creates a priced plan and confirms before removing it from public offers', async () => {
  const user = userEvent.setup()
  const plan = {
    id: 5, name: 'Explorer', price: 9, currency: 'USD', billing_period: 'monthly' as const,
    trip_limit_per_day: 3, chat_edit_limit_per_day: 5, is_active: true,
  }
  let plans = [] as typeof plan[]
  vi.mocked(adminSubscriptionPlansApi.getAdminSubscriptionPlans).mockImplementation(async () => plans)
  vi.mocked(adminSubscriptionPlansApi.createAdminSubscriptionPlan).mockImplementation(async () => {
    plans = [plan]
    return plan
  })
  vi.mocked(adminSubscriptionPlansApi.deactivateAdminSubscriptionPlan).mockResolvedValue({ ...plan, is_active: false })
  const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false)
  const { container } = render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <AdminSubscriptionPlansPage />
    </QueryClientProvider>,
  )

  await screen.findByRole('heading', { name: 'Subscription plans' })
  await user.click(screen.getAllByRole('button', { name: 'Create plan' })[0])
  const name = container.querySelector<HTMLInputElement>('input[name="name"]')
  const price = container.querySelector<HTMLInputElement>('input[name="price"]')
  const tripLimit = container.querySelector<HTMLInputElement>('input[name="trip_limit_per_day"]')
  const editLimit = container.querySelector<HTMLInputElement>('input[name="chat_edit_limit_per_day"]')
  if (!name || !price || !tripLimit || !editLimit) throw new Error('Plan form is incomplete')
  await user.type(name, 'Explorer')
  await user.clear(price)
  await user.type(price, '9')
  await user.clear(tripLimit)
  await user.type(tripLimit, '3')
  await user.clear(editLimit)
  await user.type(editLimit, '5')
  await user.click(screen.getByRole('button', { name: 'Create', exact: true }))
  await waitFor(() => expect(adminSubscriptionPlansApi.createAdminSubscriptionPlan).toHaveBeenCalledWith(
    expect.objectContaining({ name: 'Explorer', price: 9, trip_limit_per_day: 3 }),
  ))

  await screen.findByText('Explorer')
  await user.click(screen.getByRole('button', { name: 'Deactivate' }))
  expect(adminSubscriptionPlansApi.deactivateAdminSubscriptionPlan).not.toHaveBeenCalled()
  confirm.mockReturnValue(true)
  await user.click(screen.getByRole('button', { name: 'Deactivate' }))
  await waitFor(() => expect(adminSubscriptionPlansApi.deactivateAdminSubscriptionPlan).toHaveBeenCalledWith(5))
  confirm.mockRestore()
})
