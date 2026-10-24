import { afterEach, expect, test, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { BusinessAnalyticsPage } from '../../src/pages/business/BusinessAnalyticsPage'
import { businessAnalyticsApi } from '../../src/features/business/analytics/api/businessAnalytics.api'
import { sponsoredPlacesApi } from '../../src/features/business/sponsored-places/api/sponsoredPlaces.api'

vi.mock('../../src/features/business/analytics/api/businessAnalytics.api', () => ({
  businessAnalyticsApi: { getBusinessAnalyticsOverview: vi.fn(), getBusinessSponsoredPlaceAnalytics: vi.fn() },
}))
vi.mock('../../src/features/business/sponsored-places/api/sponsoredPlaces.api', () => ({
  sponsoredPlacesApi: { getSponsoredPlaces: vi.fn() },
}))
vi.mock('../../src/features/business/analytics/ui/BusinessAnalyticsInteractionsChart', () => ({
  BusinessAnalyticsInteractionsChart: () => <div>Interaction chart</div>,
}))

const renderPage = () => render(
  <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
    <MemoryRouter><BusinessAnalyticsPage /></MemoryRouter>
  </QueryClientProvider>,
)

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

test('shows overview and per-place interaction rates from live query results', async () => {
  vi.mocked(businessAnalyticsApi.getBusinessAnalyticsOverview).mockResolvedValue({
    impressions_count: 100, interactions_count: 25, interactions_by_type: { call: 10, map: 15 },
  })
  vi.mocked(businessAnalyticsApi.getBusinessSponsoredPlaceAnalytics).mockResolvedValue({
    impressions_count: 20, interactions_count: 5, interactions_by_type: { call: 5 },
  })
  vi.mocked(sponsoredPlacesApi.getSponsoredPlaces).mockResolvedValue([{
    id: 5, business_id: 3, title: 'Lake Tour', description: 'A route', city: 'Bishkek',
    category: 'tour', address: 'Square', lat: 42.87, lng: 74.56,
    contact_phone: null, website_url: null, cta_text: null, is_active: true, is_approved: true,
  }])

  renderPage()
  expect(await screen.findByText('Lake Tour')).toBeTruthy()
  await waitFor(() => expect(screen.getAllByText('25%').length).toBe(2))
  expect(businessAnalyticsApi.getBusinessSponsoredPlaceAnalytics).toHaveBeenCalledWith(5)
})

test('offers retry when overview analytics cannot be loaded', async () => {
  vi.mocked(businessAnalyticsApi.getBusinessAnalyticsOverview)
    .mockRejectedValueOnce(new Error('Analytics unavailable'))
    .mockResolvedValue({ impressions_count: 0, interactions_count: 0, interactions_by_type: {} })
  vi.mocked(sponsoredPlacesApi.getSponsoredPlaces).mockResolvedValue([])
  renderPage()

  expect(await screen.findByText('Analytics unavailable')).toBeTruthy()
  await userEvent.setup().click(screen.getByRole('button', { name: 'Retry' }))
  expect(await screen.findByText('No sponsored places yet')).toBeTruthy()
  expect(businessAnalyticsApi.getBusinessAnalyticsOverview).toHaveBeenCalledTimes(2)
})
