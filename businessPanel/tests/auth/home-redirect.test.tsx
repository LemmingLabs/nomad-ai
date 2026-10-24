import { afterEach, expect, test } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { HomeRedirectPage } from '../../src/pages/HomeRedirectPage'
import { useAuthStore } from '../../src/features/auth/model/auth.store'
import type { UserRole } from '../../src/features/auth/model/auth.types'

afterEach(() => {
  cleanup()
  useAuthStore.setState({ status: 'unauthenticated', user: null })
})

test.each([
  ['admin', 'Admin dashboard'],
  ['business', 'Business dashboard'],
  ['user', 'Sign in page'],
] as const)('routes the %s role to %s', async (role, destination) => {
  useAuthStore.setState({ status: 'authenticated', user: { id: 1, role: role as UserRole } })
  render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<HomeRedirectPage />} />
        <Route path="/admin" element={<p>Admin dashboard</p>} />
        <Route path="/business" element={<p>Business dashboard</p>} />
        <Route path="/login" element={<p>Sign in page</p>} />
      </Routes>
    </MemoryRouter>,
  )
  expect(await screen.findByText(destination)).toBeTruthy()
})
