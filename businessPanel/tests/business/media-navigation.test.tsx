import { afterEach, expect, test } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { BusinessMediaPage } from '../../src/pages/business/BusinessMediaPage'

afterEach(cleanup)

test('directs businesses from the old media page to sponsored place uploads', async () => {
  render(
    <MemoryRouter initialEntries={['/business/media']}>
      <Routes>
        <Route path="/business/media" element={<BusinessMediaPage />} />
        <Route path="/business/sponsored-places" element={<p>Sponsored place uploads</p>} />
      </Routes>
    </MemoryRouter>,
  )
  expect(screen.getByText(/media for sponsored content is now managed/i)).toBeTruthy()
  await userEvent.setup().click(screen.getByRole('button', { name: 'Open Sponsored Places' }))
  expect(await screen.findByText('Sponsored place uploads')).toBeTruthy()
})
