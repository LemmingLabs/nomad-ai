import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { LoginPage } from '../../pages/auth/login/LoginPage';
import { RegisterPage } from '../../pages/auth/register/RegisterPage';
import { loginApi } from '../../features/auth/login-by-email';
import { registerApi } from '../../features/auth/register-by-email';
import { syncGuestTripApi } from '../../features/trip/sync-guest-trip';
import { userApi } from '../../entities/user';

const setUser = vi.fn();
const addTrip = vi.fn();
const setActiveTrip = vi.fn();

vi.mock('../../features/auth/login-by-email', async (importOriginal) => ({
  ...await importOriginal<typeof import('../../features/auth/login-by-email')>(),
  loginApi: { login: vi.fn() },
}));
vi.mock('../../features/trip/sync-guest-trip', () => ({ syncGuestTripApi: { sync: vi.fn() } }));
vi.mock('../../features/auth/register-by-email', async (importOriginal) => ({
  ...await importOriginal<typeof import('../../features/auth/register-by-email')>(),
  registerApi: { register: vi.fn() },
}));
vi.mock('../../entities/user', () => ({ userApi: { getMe: vi.fn() }, useUserStore: () => ({ setUser }) }));
vi.mock('../../entities/trip', () => ({ useTripStore: () => ({ addTrip, setActiveTrip }) }));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  localStorage.clear();
});

test('signs in and claims the guest itinerary before opening its workspace', async () => {
  const user = userEvent.setup();
  const trip = { id: 42, title: 'Mountain escape' };
  const account = { id: 7, email: 'guide@example.com' };
  localStorage.setItem('guest_trip_id', '42');
  vi.mocked(loginApi.login).mockResolvedValue({ access_token: 'test-token' } as never);
  vi.mocked(userApi.getMe).mockResolvedValue(account as never);
  vi.mocked(syncGuestTripApi.sync).mockResolvedValue(trip as never);

  render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter initialEntries={['/auth/login']}>
        <Routes>
          <Route path="/auth/login" element={<LoginPage />} />
          <Route path="/trip/:id" element={<p>Trip workspace</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
  await user.type(screen.getByRole('textbox', { name: 'Email' }), 'guide@example.com');
  await user.type(screen.getByLabelText('Password'), 'secret123');
  await user.click(screen.getByRole('button', { name: 'Sign In' }));

  expect(await screen.findByText('Trip workspace')).toBeTruthy();
  expect(loginApi.login).toHaveBeenCalledWith({ email: 'guide@example.com', password: 'secret123' }, expect.anything());
  expect(syncGuestTripApi.sync).toHaveBeenCalledWith({ trip_id: 42 });
  expect(setUser).toHaveBeenCalledWith(account);
  expect(addTrip).toHaveBeenCalledWith(trip);
  expect(setActiveTrip).toHaveBeenCalledWith(42);
  expect(localStorage.getItem('guest_trip_id')).toBeNull();
  expect(localStorage.getItem('access_token')).toBe('test-token');
});

test('creates an account and carries the guest trip into it', async () => {
  const user = userEvent.setup();
  const trip = { id: 99, title: 'Lake weekend' };
  localStorage.setItem('guest_trip_id', '99');
  vi.mocked(registerApi.register).mockResolvedValue({} as never);
  vi.mocked(loginApi.login).mockResolvedValue({ access_token: 'new-token' } as never);
  vi.mocked(userApi.getMe).mockResolvedValue({ id: 8, email: 'new@example.com' } as never);
  vi.mocked(syncGuestTripApi.sync).mockResolvedValue(trip as never);

  render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter initialEntries={['/auth/register']}>
        <Routes>
          <Route path="/auth/register" element={<RegisterPage />} />
          <Route path="/trip/:id" element={<p>Trip workspace</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
  await user.type(screen.getByRole('textbox', { name: 'Email' }), 'new@example.com');
  await user.type(screen.getByLabelText('Password'), 'secret123');
  await user.type(screen.getByLabelText('Confirm password'), 'secret123');
  await user.click(screen.getByRole('button', { name: 'Create Account' }));

  expect(await screen.findByText('Trip workspace')).toBeTruthy();
  expect(registerApi.register).toHaveBeenCalledWith({ email: 'new@example.com', password: 'secret123' });
  expect(syncGuestTripApi.sync).toHaveBeenCalledWith({ trip_id: 99 });
  expect(setActiveTrip).toHaveBeenCalledWith(99);
  expect(localStorage.getItem('guest_trip_id')).toBeNull();
});
