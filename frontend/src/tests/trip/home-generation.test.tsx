import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { HomePage } from '../../pages/home/HomePage';
import { generateTripApi } from '../../features/trip/generate-trip';

const addTrip = vi.fn();
const setActiveTrip = vi.fn();

vi.mock('../../entities/trip', () => ({ useTripStore: () => ({ addTrip, setActiveTrip }) }));
vi.mock('../../entities/user', () => ({ useUserStore: () => ({ isAuthenticated: false }) }));
vi.mock('../../entities/destination', () => ({
  useDestinationsQuery: () => ({
    data: [{ id: 'kg', country_code: 'KG', country_name: 'Kyrgyzstan', name: 'Kyrgyzstan', enabled: true }],
    isLoading: false,
    isError: false,
  }),
}));
vi.mock('../../entities/limit', () => ({
  useMyLimitsQuery: () => ({ data: null }),
  limitQueryKeys: { me: () => ['limits', 'me'] },
}));
vi.mock('../../features/ui/open-sidebar', () => ({ useSidebarStore: () => ({ isOpen: false }) }));
vi.mock('../../shared/hooks', () => ({ useMediaQuery: () => false }));
vi.mock('../../widgets/sidebar', () => ({ Sidebar: () => <aside>Trips sidebar</aside> }));
vi.mock('../../widgets/limit-reached-modal', () => ({ LimitReachedModal: () => null }));
vi.mock('../../features/trip/generate-trip', async (importOriginal) => {
  const original = await importOriginal<typeof import('../../features/trip/generate-trip')>();
  return { ...original, generateTripApi: { generate: vi.fn() } };
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  localStorage.clear();
});

test('creates a guest trip, saves its identifier, and opens the trip workspace', async () => {
  const trip = { id: 42, title: 'Mountain escape' };
  vi.mocked(generateTripApi.generate).mockResolvedValue(trip as never);
  const user = userEvent.setup();
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

  render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/trip/:id" element={<p>Trip workspace</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );

  await user.click(screen.getByRole('button', { name: 'Create a trip' }));
  await user.type(screen.getByRole('textbox', { name: /prompt/i }), '  Quiet lakes  ');
  await user.click(screen.getByRole('button', { name: /generate itinerary/i }));

  expect(await screen.findByText('Trip workspace')).toBeTruthy();
  expect(vi.mocked(generateTripApi.generate).mock.calls[0][0]).toEqual(expect.objectContaining({
    budget: 'medium',
    interests: ['nature', 'culture'],
    prompt: 'Quiet lakes',
    country_code: 'KG',
    destination_id: 'kg',
  }));
  expect(addTrip).toHaveBeenCalledWith(trip);
  expect(setActiveTrip).toHaveBeenCalledWith(42);
  expect(localStorage.getItem('guest_trip_id')).toBe('42');
});
