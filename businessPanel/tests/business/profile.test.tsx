import { afterEach, expect, test, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BusinessProfilePage } from '../../src/pages/business/BusinessProfilePage'
import { businessProfileApi } from '../../src/features/business/profile/api/businessProfile.api'

vi.mock('../../src/features/business/profile/api/businessProfile.api', () => ({
  businessProfileApi: {
    getBusinessProfile: vi.fn(),
    createBusinessProfile: vi.fn(),
    updateBusinessProfile: vi.fn(),
  },
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

test('creates a business profile and then edits its details', async () => {
  const user = userEvent.setup()
  let profile: { id: number; name: string; description: string | null; contact_phone: string | null; website_url: string | null } | null = null
  vi.mocked(businessProfileApi.getBusinessProfile).mockImplementation(async () => profile)
  vi.mocked(businessProfileApi.createBusinessProfile).mockImplementation(async (payload) => {
    profile = { id: 3, ...payload }
    return profile
  })
  vi.mocked(businessProfileApi.updateBusinessProfile).mockImplementation(async (payload) => {
    profile = { ...profile!, ...payload }
    return profile
  })

  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <BusinessProfilePage />
    </QueryClientProvider>,
  )

  await screen.findByRole('button', { name: 'Create profile' })
  await user.type(screen.getByPlaceholderText('Business name'), '  Nomad Guides  ')
  await user.type(screen.getByPlaceholderText('Describe your business'), 'Local walks')
  await user.click(screen.getByRole('button', { name: 'Create profile' }))
  await waitFor(() => expect(businessProfileApi.createBusinessProfile).toHaveBeenCalledWith({
    name: 'Nomad Guides', description: 'Local walks', contact_phone: null, website_url: null,
  }))

  await screen.findByRole('button', { name: 'Save changes' })
  await user.clear(screen.getByPlaceholderText('Describe your business'))
  await user.type(screen.getByPlaceholderText('Describe your business'), 'Tailored city routes')
  await user.click(screen.getByRole('button', { name: 'Save changes' }))
  await waitFor(() => expect(businessProfileApi.updateBusinessProfile).toHaveBeenCalledWith(
    expect.objectContaining({ description: 'Tailored city routes' }),
  ))
})
