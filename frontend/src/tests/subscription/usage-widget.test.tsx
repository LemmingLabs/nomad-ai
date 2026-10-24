import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { UsageWidget } from '../../widgets/usage-widget/UsageWidget';

const state = vi.hoisted(() => ({ authenticated: false }));

vi.mock('../../entities/user', () => ({ useUserStore: () => ({ isAuthenticated: state.authenticated }) }));
vi.mock('../../entities/limit', () => ({
  useMyLimitsQuery: () => ({
    isLoading: false,
    data: state.authenticated ? {
      plan: 'PRO', trip_generations_used: 2, trip_limit_per_day: 5,
      chat_edits_used: 1, chat_edit_limit_per_day: 10,
    } : null,
  }),
}));
vi.mock('../../entities/subscription', async (importOriginal) => ({
  ...await importOriginal<typeof import('../../entities/subscription')>(),
  useMySubscriptionQuery: () => ({ isLoading: false, data: null }),
}));

afterEach(() => {
  cleanup();
  state.authenticated = false;
});

test('invites guests to sign in before showing personal usage', () => {
  render(<MemoryRouter><UsageWidget /></MemoryRouter>);
  expect(screen.getByText(/sign in to track your daily limits/i)).toBeTruthy();
  expect(screen.getByRole('link', { name: 'Sign in' }).getAttribute('href')).toBe('/auth/login');
  expect(screen.queryByText(/trip generations left/i)).toBeNull();
});

test('shows the remaining daily quota for a signed-in traveler', () => {
  state.authenticated = true;
  render(<MemoryRouter><UsageWidget /></MemoryRouter>);
  expect(screen.getByText('3 trip generations left.')).toBeTruthy();
  expect(screen.getByRole('link', { name: 'Upgrade' }).getAttribute('href')).toBe('/pricing');
  expect(screen.getByRole('link', { name: 'Details' }).getAttribute('href')).toBe('/profile');
});
