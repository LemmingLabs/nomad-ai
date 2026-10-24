import { afterEach, expect, test, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { BusinessDashboardPage } from '../../src/pages/business/BusinessDashboardPage'
import { businessProfileApi } from '../../src/features/business/profile/api/businessProfile.api'
import { sponsoredPlacesApi } from '../../src/features/business/sponsored-places/api/sponsoredPlaces.api'
import { businessAnalyticsApi } from '../../src/features/business/analytics/api/businessAnalytics.api'

vi.mock('../../src/features/business/profile/api/businessProfile.api', () => ({
  businessProfileApi: { getBusinessProfile: vi.fn() },
}))
vi.mock('../../src/features/business/sponsored-places/api/sponsoredPlaces.api', () => ({
  sponsoredPlacesApi: { getSponsoredPlaces: vi.fn() },
}))
vi.mock('../../src/features/business/analytics/api/businessAnalytics.api', () => ({
  businessAnalyticsApi: { getBusinessAnalyticsOverview: vi.fn() },
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

test('summarizes place status and opens the management workspace', async () => {
  vi.mocked(businessProfileApi.getBusinessProfile).mockResolvedValue({
    id: 3, name: 'Nomad Guides', description: null, contact_phone: null,
    website_url: null, is_active: true,
  })
  vi.mocked(sponsoredPlacesApi.getSponsoredPlaces).mockResolvedValue([
    { id: 1, business_id: 3, title: 'Lake Tour', description: 'Lake', city: 'Bishkek', category: 'tour', address: 'Square', lat: 42.8, lng: 74.5, contact_phone: null, website_url: null, cta_text: null, is_active: true, is_approved: false },
    { id: 2, business_id: 3, title: 'Old Town', description: 'City', city: 'Bishkek', category: 'walk', address: 'Center', lat: 42.8, lng: 74.6, contact_phone: null, website_url: null, cta_text: null, is_active: false, is_approved: true },
  ])
  vi.mocked(businessAnalyticsApi.getBusinessAnalyticsOverview).mockResolvedValue({
    impressions_count: 200, interactions_count: 10, interactions_by_type: { call: 10 },
  })
  const user = userEvent.setup()

  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={['/business']}>
        <Routes>
          <Route path="/business" element={<BusinessDashboardPage />} />
          <Route path="/business/sponsored-places" element={<p>Sponsored management</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )

  expect(await screen.findByText('Nomad Guides')).toBeTruthy()
  expect(screen.getByText('5%')).toBeTruthy()
  expect(screen.getByText('Pending approval')).toBeTruthy()
  await user.click(screen.getByRole('button', { name: 'Manage' }))
  expect(await screen.findByText('Sponsored management')).toBeTruthy()
})
