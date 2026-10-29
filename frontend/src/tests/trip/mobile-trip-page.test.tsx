import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { TripPage } from '../../pages/trip/TripPage';

const session = vi.hoisted(() => ({ authenticated: false }));
const trip = { id: 42, title: 'Lake trip', itinerary_json: { days: [{ day: 1 }] } };
vi.mock('../../entities/trip', () => ({
  tripApi: { getById: () => Promise.resolve({ trip, messages: { items: [] } }) },
  useTripStore: () => ({ trips: [trip], setActiveTrip: vi.fn(), updateTrip: vi.fn(), updateTripItinerary: vi.fn() }),
}));
vi.mock('../../entities/message', () => ({ messageApi: { send: vi.fn() } }));
vi.mock('../../entities/user', () => ({ useUserStore: () => ({ isAuthenticated: session.authenticated }) }));
vi.mock('../../entities/limit', () => ({
  useMyLimitsQuery: () => ({ data: { chat_edits_used: 0, chat_edit_limit_per_day: 5 } }), limitQueryKeys: { me: () => ['limits', 'me'] },
}));
vi.mock('../../features/ui/open-sidebar', () => ({
  useSidebarStore: () => ({ isOpen: false, isCollapsed: false, setCollapsed: vi.fn() }),
}));
vi.mock('../../shared/hooks', () => ({ useMediaQuery: () => true }));
vi.mock('../../widgets/sidebar', () => ({ Sidebar: () => null }));
vi.mock('../../widgets/chat-panel', () => ({
  ChatPanel: ({ isDisabled }: { isDisabled: boolean }) => <textarea aria-label="Message" disabled={isDisabled} />,
}));
vi.mock('../../widgets/trip-preview', () => ({
  TripPreview: ({ actions }: { actions: React.ReactNode }) => <div><h2>Lake itinerary</h2>{actions}</div>,
}));

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

test.each([false, true])('mobile itinerary and chat are reachable (authenticated: %s)', async (authenticated) => {
  session.authenticated = authenticated;
  const print = vi.fn();
  vi.stubGlobal('print', print);
  const user = userEvent.setup();
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={['/trip/42']}>
        <Routes><Route path="/trip/:id" element={<TripPage />} /></Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
  expect(await screen.findByRole('heading', { name: 'Lake itinerary' })).toBeTruthy();
  await user.click(screen.getByRole('button', { name: 'Print itinerary' }));
  expect(print).toHaveBeenCalledOnce();
  await user.click(screen.getByRole('button', { name: 'Chat' }));
  await waitFor(() => expect(screen.getByRole('textbox', { name: 'Message' }).hasAttribute('disabled')).toBe(!authenticated));
  await user.click(screen.getByRole('button', { name: 'Itinerary' }));
  expect(screen.getByRole('heading', { name: 'Lake itinerary' })).toBeTruthy();
});
