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

test('submits flight search inputs and displays disabled provider response without inventing prices', async () => {
  const user = userEvent.setup()
  vi.mocked(offersApi.search).mockRejectedValue({
    response: { data: { state: 'unavailable', reason: 'feature_disabled', message: 'Flight and stay offers are not available yet.' } },
  })
  renderPanel()

  await user.type(screen.getByLabelText('Origin airport or city'), 'ALA')
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

test('loads local OurAirports suggestions in the development environment', async () => {
  renderPanel()

  expect(await screen.findByText(/Development airport suggestions from OurAirports/)).toBeTruthy()
  expect(document.querySelector('datalist option[value="ALA — Almaty"]')).toBeTruthy()
})
