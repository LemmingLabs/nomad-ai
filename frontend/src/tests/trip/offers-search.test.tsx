import { afterEach, expect, test, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { OffersSearchPanel } from '../../widgets/offers-search/OffersSearchPanel'
import { offersApi } from '../../entities/offers'

vi.mock('../../entities/offers', () => ({
  offersApi: { search: vi.fn() },
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

function renderPanel() {
  return render(<OffersSearchPanel countryCode="KG" destinationCity="Bishkek" />)
}

function liveOffer(overrides: Partial<{
  id: string
  kind: 'flight' | 'stay'
  provider: string
  fetched_at: string
  expires_at: string
  currency: string
  total_amount: number | string
  availability: 'available' | 'limited'
  conditions: string[]
  handoff_url: string
}> = {}) {
  const now = Date.now()
  return {
    id: 'provider-flight-1',
    kind: 'flight' as const,
    provider: 'TestSupplier',
    fetched_at: new Date(now - 1000).toISOString(),
    expires_at: new Date(now + 60_000).toISOString(),
    currency: 'USD',
    total_amount: '312.45',
    availability: 'available' as const,
    conditions: ['1 checked bag included', 'Non-refundable'],
    handoff_url: 'https://supplier.example/offers/provider-flight-1',
    ...overrides,
  }
}

test('submits flight search inputs and displays disabled provider response without inventing prices', async () => {
  const user = userEvent.setup()
  vi.mocked(offersApi.search).mockRejectedValue({
    response: { data: { state: 'unavailable', reason: 'feature_disabled', message: 'Flight and stay offers are not available yet.' } },
  })
  renderPanel()

  await user.type(screen.getByLabelText('Origin airport or city'), 'ALA — Almaty')
  await user.click(screen.getByRole('button', { name: 'Search flights' }))

  expect((await screen.findByRole('status')).textContent).toContain('Flight and stay offers are not available yet.')
  expect(offersApi.search).toHaveBeenCalledWith(expect.objectContaining({
    kind: 'flight',
    destination_country_code: 'KG',
    origin: 'ALA',
    destination: 'Bishkek',
    passengers: 1,
  }))
  expect(screen.queryByText(/\$|€|KGS|USD/)).toBeNull()
})

test('switches to stay search and reports the provider-unconfigured state', async () => {
  const user = userEvent.setup()
  vi.mocked(offersApi.search).mockRejectedValue({
    response: { data: { state: 'unavailable', reason: 'provider_unconfigured', message: 'No approved offers provider is configured.' } },
  })
  renderPanel()

  await user.click(screen.getByRole('tab', { name: 'Stays' }))
  await user.click(screen.getByRole('button', { name: 'Search stays' }))

  expect((await screen.findByRole('status')).textContent).toContain('No approved offers provider is configured.')
  expect(offersApi.search).toHaveBeenCalledWith(expect.objectContaining({
    kind: 'stay',
    destination_country_code: 'KG',
    destination_city: 'Bishkek',
    adults: 1,
    rooms: 1,
  }))
})

test('shows clearly labeled demo examples without a supplier handoff', async () => {
  const user = userEvent.setup()
  vi.mocked(offersApi.search).mockResolvedValue({
    state: 'demo',
    message: 'Development demo only: example totals are not live prices, availability is not checked, and these results cannot be booked.',
    offers: [{
      id: 'demo-flight-1',
      kind: 'flight',
      title: 'Sample flight: ALA to Bishkek',
      source: 'NomadAI demo fixture',
      example_total: 250,
      currency: 'USD',
      conditions: 'Illustrative example only; no availability or booking link has been checked.',
      handoff_url: null,
    }],
  })
  renderPanel()

  await user.type(screen.getByLabelText('Origin airport or city'), 'ALA')
  await user.click(screen.getByRole('button', { name: 'Search flights' }))

  expect((await screen.findByText('DEVELOPMENT DEMO · NOT BOOKABLE')).textContent).toContain('DEVELOPMENT DEMO')
  expect(screen.getByText('Sample flight: ALA to Bishkek')).toBeTruthy()
  expect(screen.getByText(/Example total:/).textContent).toContain('$250.00')
  expect(screen.getByText('NomadAI demo fixture · no supplier link')).toBeTruthy()
})

test('renders live provider, checked time, conditions, and external handoff', async () => {
  const user = userEvent.setup()
  vi.mocked(offersApi.search).mockResolvedValue({
    state: 'results',
    provider: 'TestSupplier',
    offers: [liveOffer()],
  })
  renderPanel()

  await user.type(screen.getByLabelText('Origin airport or city'), 'ALA')
  await user.click(screen.getByRole('button', { name: 'Search flights' }))

  expect(await screen.findByText('TestSupplier · reference provider-flight-1')).toBeTruthy()
  expect(screen.getByText('$312.45')).toBeTruthy()
  expect(screen.getByText(/1 checked bag included · Non-refundable/)).toBeTruthy()
  expect(screen.getByText(/^Checked /)).toBeTruthy()
  const handoff = screen.getByRole('link', { name: 'Continue to TestSupplier' })
  expect(handoff.getAttribute('href')).toBe('https://supplier.example/offers/provider-flight-1')
  expect(handoff.getAttribute('target')).toBe('_blank')
  expect(handoff.getAttribute('rel')).toBe('noopener noreferrer')
})

test('shows a clear no-results state without leaving a price visible', async () => {
  const user = userEvent.setup()
  vi.mocked(offersApi.search).mockResolvedValue({
    state: 'no_results',
    provider: 'TestSupplier',
    fetched_at: new Date().toISOString(),
  })
  renderPanel()

  await user.type(screen.getByLabelText('Origin airport or city'), 'ALA')
  await user.click(screen.getByRole('button', { name: 'Search flights' }))

  expect((await screen.findByRole('status')).textContent).toContain('No flights were found')
  expect(screen.queryByText('$312.45')).toBeNull()
  expect(screen.queryByRole('link', { name: /Continue to/ })).toBeNull()
})

test('hides an expired supplier price and handoff link', async () => {
  const user = userEvent.setup()
  vi.mocked(offersApi.search).mockResolvedValue({
    state: 'results',
    provider: 'TestSupplier',
    offers: [liveOffer({
      fetched_at: new Date(Date.now() - 2 * 60 * 60_000).toISOString(),
      expires_at: new Date(Date.now() - 60_000).toISOString(),
    })],
  })
  renderPanel()

  await user.type(screen.getByLabelText('Origin airport or city'), 'ALA')
  await user.click(screen.getByRole('button', { name: 'Search flights' }))

  expect(await screen.findByText('Price expired')).toBeTruthy()
  expect(screen.getByText(/Search again to check the price and availability/)).toBeTruthy()
  expect(screen.queryByText('$312.45')).toBeNull()
  expect(screen.queryByRole('link', { name: 'Continue to TestSupplier' })).toBeNull()
})

test('clears live results when search inputs change', async () => {
  const user = userEvent.setup()
  vi.mocked(offersApi.search).mockResolvedValue({
    state: 'results',
    provider: 'TestSupplier',
    offers: [liveOffer()],
  })
  renderPanel()

  await user.type(screen.getByLabelText('Origin airport or city'), 'ALA')
  await user.click(screen.getByRole('button', { name: 'Search flights' }))
  expect(await screen.findByText('$312.45')).toBeTruthy()

  await user.type(screen.getByLabelText('Origin airport or city'), 'B')
  expect(screen.queryByText('$312.45')).toBeNull()
  expect(screen.queryByRole('link', { name: 'Continue to TestSupplier' })).toBeNull()
})

test('loads local OurAirports suggestions in the development environment', async () => {
  renderPanel()

  expect(await screen.findByText(/Development airport suggestions from OurAirports/)).toBeTruthy()
  expect(document.querySelector('datalist option[value="ALA — Almaty"]')).toBeTruthy()
})
