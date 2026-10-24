import { afterEach, expect, test, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BusinessSponsoredPlacesPage } from '../../src/pages/business/BusinessSponsoredPlacesPage'
import { sponsoredPlacesApi } from '../../src/features/business/sponsored-places/api/sponsoredPlaces.api'

vi.mock('../../src/features/business/sponsored-places/api/sponsoredPlaces.api', () => ({
  sponsoredPlacesApi: {
    getSponsoredPlaces: vi.fn(),
    createSponsoredPlace: vi.fn(),
    updateSponsoredPlace: vi.fn(),
    deleteSponsoredPlace: vi.fn(),
  },
}))
vi.mock('../../src/features/business/sponsored-places/ui/SponsoredPlaceLocationPicker', () => ({
  SponsoredPlaceLocationPicker: ({ onChange }: {
    onChange: (location: { lat: string; lng: string; address: string; city: string }) => void
  }) => <button type="button" onClick={() => onChange({
    lat: '42.8746', lng: '74.5698', address: 'Ala-Too Square', city: 'Bishkek',
  })}>Select Bishkek</button>,
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

const place = {
  id: 17, business_id: 3, title: 'City Walk', description: 'Guided route', city: 'Bishkek',
  category: 'culture', address: 'Ala-Too Square', lat: 42.8746, lng: 74.5698,
  contact_phone: null, website_url: null, cta_text: null, is_active: true, is_approved: false,
}

test('creates a sponsored place with map coordinates and refreshes the list', async () => {
  const user = userEvent.setup()
  let places = [] as typeof place[]
  vi.mocked(sponsoredPlacesApi.getSponsoredPlaces).mockImplementation(async () => places)
  vi.mocked(sponsoredPlacesApi.createSponsoredPlace).mockImplementation(async () => {
    places = [place]
    return place
  })

  const { container } = render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <BusinessSponsoredPlacesPage />
    </QueryClientProvider>,
  )

  await screen.findByRole('heading', { name: 'No sponsored places yet' })
  await user.click(screen.getAllByRole('button', { name: 'Create' })[0])
  await user.click(screen.getByRole('button', { name: 'Select Bishkek' }))
  const title = container.querySelector<HTMLInputElement>('input[name="title"]')
  const description = container.querySelector<HTMLTextAreaElement>('textarea[name="description"]')
  const category = container.querySelector<HTMLInputElement>('input[name="category"]')
  if (!title || !description || !category) throw new Error('Sponsored place form is incomplete')
  await user.type(title, ' City Walk ')
  await user.type(description, 'Guided route')
  await user.type(category, 'culture')
  const createButtons = screen.getAllByRole('button', { name: 'Create' })
  await user.click(createButtons[createButtons.length - 1])

  await waitFor(() => expect(sponsoredPlacesApi.createSponsoredPlace).toHaveBeenCalledOnce())
  expect(vi.mocked(sponsoredPlacesApi.createSponsoredPlace).mock.calls[0][0]).toMatchObject({
    title: 'City Walk', city: 'Bishkek', lat: 42.8746, lng: 74.5698,
  })
  expect(await screen.findByText('City Walk')).toBeTruthy()
})

test('edits a place and asks for confirmation before deactivation', async () => {
  const user = userEvent.setup()
  vi.mocked(sponsoredPlacesApi.getSponsoredPlaces).mockResolvedValue([place])
  vi.mocked(sponsoredPlacesApi.updateSponsoredPlace).mockResolvedValue(place)
  vi.mocked(sponsoredPlacesApi.deleteSponsoredPlace).mockResolvedValue(undefined)
  const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false)
  const { container } = render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <BusinessSponsoredPlacesPage />
    </QueryClientProvider>,
  )

  await user.click(await screen.findByRole('button', { name: 'Edit' }))
  const title = container.querySelector<HTMLInputElement>('input[name="title"]')
  if (!title) throw new Error('Edit form has no title field')
  await user.clear(title)
  await user.type(title, 'Updated Walk')
  await user.click(screen.getByRole('button', { name: 'Save changes' }))
  await waitFor(() => expect(sponsoredPlacesApi.updateSponsoredPlace).toHaveBeenCalledWith(
    17, expect.objectContaining({ title: 'Updated Walk' }),
  ))

  await user.click(screen.getByRole('button', { name: 'Deactivate' }))
  expect(sponsoredPlacesApi.deleteSponsoredPlace).not.toHaveBeenCalled()
  confirm.mockReturnValue(true)
  await user.click(screen.getByRole('button', { name: 'Deactivate' }))
  await waitFor(() => expect(sponsoredPlacesApi.deleteSponsoredPlace).toHaveBeenCalledWith(17))
  confirm.mockRestore()
})
