import { afterEach, expect, test, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { LoginPage } from '../../src/pages/LoginPage'
import { authApi } from '../../src/features/auth/api/auth.api'
import { useAuthStore } from '../../src/features/auth/model/auth.store'

vi.mock('../../src/features/auth/api/auth.api', () => ({
  authApi: { login: vi.fn(), getMe: vi.fn() },
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
  localStorage.clear()
  useAuthStore.setState({ status: 'unauthenticated', user: null })
})

test('sends a business user to the business workspace instead of an admin return path', async () => {
  useAuthStore.setState({ status: 'unauthenticated', user: null })
  vi.mocked(authApi.login).mockResolvedValue({
    accessToken: 'business-token', user: { id: 3, role: 'business' },
  })
  const user = userEvent.setup()

  render(
    <MemoryRouter initialEntries={[{ pathname: '/login', state: { from: { pathname: '/admin/review' } } }]}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/business" element={<p>Business workspace</p>} />
        <Route path="/admin/review" element={<p>Admin review</p>} />
      </Routes>
    </MemoryRouter>,
  )
  await user.type(screen.getByRole('textbox', { name: 'Email' }), 'owner@example.com')
  await user.type(screen.getByLabelText('Password'), 'secret')
  await user.click(screen.getByRole('button', { name: 'Sign in' }))

  expect(await screen.findByText('Business workspace')).toBeTruthy()
  expect(screen.queryByText('Admin review')).toBeNull()
  expect(authApi.login).toHaveBeenCalledWith({ email: 'owner@example.com', password: 'secret' })
  expect(localStorage.getItem('nomadai.auth.accessToken')).toBe('business-token')
})
