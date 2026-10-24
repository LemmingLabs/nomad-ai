import { afterEach, expect, test, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LoginForm } from '../../src/features/auth/ui/LoginForm'

afterEach(cleanup)

test('requires credentials before submitting', async () => {
  const submit = vi.fn()
  render(<LoginForm onSubmit={submit} />)
  await userEvent.setup().click(screen.getByRole('button', { name: 'Sign in' }))

  expect(await screen.findByText('Email is required')).toBeTruthy()
  expect(screen.getByText('Password is required')).toBeTruthy()
  expect(submit).not.toHaveBeenCalled()
})

test('submits credentials and shows server feedback', async () => {
  const submit = vi.fn()
  const user = userEvent.setup()
  render(<LoginForm onSubmit={submit} errorMessage="Invalid credentials" />)

  await user.type(screen.getByRole('textbox', { name: 'Email' }), 'guide@example.com')
  await user.type(screen.getByLabelText('Password'), 'secret')
  await user.click(screen.getByRole('button', { name: 'Sign in' }))

  expect(await screen.findByText('Invalid credentials')).toBeTruthy()
  expect(submit).toHaveBeenCalledWith({ email: 'guide@example.com', password: 'secret' }, expect.anything())
})
