import { afterEach, expect, test, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AdminModerationPage } from '../../src/pages/admin/AdminModerationPage'
import { adminSponsoredModerationApi } from '../../src/features/admin/sponsored-moderation/api/adminSponsoredModeration.api'

vi.mock('../../src/features/admin/sponsored-moderation/api/adminSponsoredModeration.api', () => ({
  adminSponsoredModerationApi: {
    getAdminSponsoredPlaces: vi.fn(),
    getAdminSponsoredPlaceDetails: vi.fn(),
    approveAdminSponsoredPlace: vi.fn(),
    rejectAdminSponsoredPlace: vi.fn(),
    activateAdminSponsoredPlace: vi.fn(),
    deactivateAdminSponsoredPlace: vi.fn(),
  },
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

test('approves a pending sponsored place after confirmation', async () => {
  const user = userEvent.setup()
  let place = {
    id: 21, business_id: 3, title: 'Lake Tour', description: 'Day trip', city: 'Bishkek',
    country_code: 'KG', region: 'Chuy', operating_language: 'en', location_verified: true,
    lat: 42.87, lng: 74.56, category: 'tour', address: 'Ala-Too Square',
    contact_phone: null, website_url: null, cta_text: null, is_active: true, is_approved: false,
  }
  vi.mocked(adminSponsoredModerationApi.getAdminSponsoredPlaces).mockImplementation(async (filters) =>
    filters?.preset === 'approved' && !place.is_approved ? [] : [place],
  )
  vi.mocked(adminSponsoredModerationApi.getAdminSponsoredPlaceDetails).mockImplementation(async () => place)
  vi.mocked(adminSponsoredModerationApi.approveAdminSponsoredPlace).mockImplementation(async () => {
    place = { ...place, is_approved: true }
    return place
  })
  const confirm = vi.spyOn(window, 'confirm').mockReturnValue(true)

  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <AdminModerationPage />
    </QueryClientProvider>,
  )

  await user.click(await screen.findByRole('button', { name: 'Approve' }))
  await waitFor(() => expect(adminSponsoredModerationApi.approveAdminSponsoredPlace).toHaveBeenCalledWith(21))
  expect(confirm).toHaveBeenCalledWith('Approve this sponsored place?')
  await user.click(screen.getByRole('button', { name: 'Approved' }))
  expect(await screen.findByRole('button', { name: 'Deactivate' })).toBeTruthy()
  confirm.mockRestore()
})
