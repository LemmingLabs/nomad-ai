import { afterEach, expect, test, vi } from 'vitest';
import { act, cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Link, MemoryRouter, Route, Routes } from 'react-router-dom';
import { TripPage } from '../../pages/trip/TripPage';
import { tripApi } from '../../entities/trip';
import { messageApi } from '../../entities/message';
import { handleApiError } from '../../shared/lib';

const setActiveTrip = vi.fn();
const updateTrip = vi.fn();
const updateTripItinerary = vi.fn();
const setCollapsed = vi.fn();
const session = vi.hoisted(() => ({ authenticated: true, trips: [] as unknown[] }));

vi.mock('../../entities/trip', () => ({
  tripApi: { getById: vi.fn() },
  useTripStore: () => ({ trips: session.trips, setActiveTrip, updateTrip, updateTripItinerary }),
}));
vi.mock('../../entities/message', () => ({ messageApi: { send: vi.fn() } }));
vi.mock('../../entities/user', () => ({ useUserStore: () => ({ isAuthenticated: session.authenticated }) }));
vi.mock('../../entities/limit', () => ({
  useMyLimitsQuery: () => ({ data: { chat_edits_used: 0, chat_edit_limit_per_day: 5 } }),
  limitQueryKeys: { me: () => ['limits', 'me'] },
}));
vi.mock('../../features/ui/open-sidebar', () => ({
  useSidebarStore: () => ({ isOpen: true, isCollapsed: false, setCollapsed }),
}));
vi.mock('../../shared/hooks', () => ({ useMediaQuery: () => false }));
vi.mock('../../shared/lib', () => ({ handleApiError: vi.fn(), getErrorMessage: () => 'Unable to load trip' }));
vi.mock('../../widgets/sidebar', () => ({ Sidebar: () => null }));
vi.mock('../../widgets/resizable-layout', () => ({
  ResizableLayout: ({ left, right }: { left: React.ReactNode; right: React.ReactNode }) => <>{left}{right}</>,
}));
vi.mock('../../widgets/chat-panel', () => ({
  ChatPanel: ({ messages, onSend, isDisabled }: {
    messages: { content: string }[]; onSend: (content: string) => void; isDisabled: boolean;
  }) => <div>
    {messages.map((message, index) => <p key={index}>{message.content}</p>)}
    <button disabled={isDisabled} onClick={() => onSend('Add a lake stop')}>Send edit</button>
  </div>,
}));
vi.mock('../../widgets/trip-preview', () => ({
  TripPreview: ({ itinerary, actions }: { itinerary: { days?: unknown[] } | null; actions: React.ReactNode }) =>
    <div><p>{itinerary?.days?.length ?? 0} route days</p>{actions}</div>,
}));
vi.mock('../../features/subscription/view-usage', async (importOriginal) => ({
  ...await importOriginal<typeof import('../../features/subscription/view-usage')>(),
  ChatEditLimitNotice: () => null,
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  session.authenticated = true;
  session.trips = [];
});

test('switches between guest trips without fetching a signed-in trip', async () => {
  session.authenticated = false;
  session.trips = [
    { id: 42, itinerary_json: { days: [{}] } },
    { id: 43, itinerary_json: { days: [{}, {}, {}] } },
  ];
  const user = userEvent.setup();
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={['/trip/42']}>
        <Link to="/trip/43">Trip B</Link>
        <Routes><Route path="/trip/:id" element={<TripPage />} /></Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
  expect(screen.getByText('1 route days')).toBeTruthy();
  await user.click(screen.getByRole('link', { name: 'Trip B' }));
  expect(screen.getByText('3 route days')).toBeTruthy();
  expect(tripApi.getById).not.toHaveBeenCalled();
});

test('loads a saved trip and applies an AI chat edit to the route', async () => {
  const originalItinerary = { days: [{ title: 'Day one' }] };
  const updatedItinerary = { days: [{ title: 'Day one' }, { title: 'Lake day' }] };
  const trip = { id: 42, title: 'Mountain escape', itinerary_json: originalItinerary };
  vi.mocked(tripApi.getById).mockResolvedValue({ trip, messages: { items: [] } } as never);
  vi.mocked(messageApi.send).mockResolvedValue({
    message: { id: 8, trip_id: 42, role: 'assistant', content: 'Added a lake stop' },
    updated_itinerary: updatedItinerary,
  } as never);
  const user = userEvent.setup();

  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={['/trip/42']}>
        <Routes><Route path="/trip/:id" element={<TripPage />} /></Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );

  expect(await screen.findByText('1 route days')).toBeTruthy();
  expect(setActiveTrip).toHaveBeenCalledWith(42);
  await user.click(screen.getByRole('button', { name: 'Send edit' }));
  expect(await screen.findByText('Added a lake stop')).toBeTruthy();
  expect(screen.getByText('2 route days')).toBeTruthy();
  expect(messageApi.send).toHaveBeenCalledWith(42, { content: 'Add a lake stop' });
  expect(updateTripItinerary).toHaveBeenCalledWith(42, updatedItinerary);
  await user.click(screen.getByRole('button', { name: 'Focus route' }));
  await waitFor(() => expect(setCollapsed).toHaveBeenCalledWith(true));
});

test('keeps a delayed edit tied to its original trip when navigating away and back', async () => {
  const tripA = { id: 42, title: 'A', itinerary_json: { days: [{ title: 'A day' }] } };
  const tripB = { id: 43, title: 'B', itinerary_json: { days: [{}, {}, {}] } };
  const updated = { days: [
    { day: 1, title: 'A day', city: 'Bishkek', location: 'A', activities: [] },
    { day: 2, title: 'Lake day', city: 'Karakol', location: 'Lake', activities: [] },
  ] };
  let currentA: { id: number; title: string; itinerary_json: { days: object[] } } = tripA;
  let aUpdated = false;
  vi.mocked(tripApi.getById).mockImplementation((id) => Promise.resolve({
    trip: id === 42 ? currentA : tripB,
    messages: { items: [{ id, trip_id: id, role: 'assistant', content: id === 42 && aUpdated ? 'A updated' : `History ${id}` }] },
  } as never));
  let finishEdit!: (value: Awaited<ReturnType<typeof messageApi.send>>) => void;
  vi.mocked(messageApi.send).mockImplementation(() => new Promise((resolve) => { finishEdit = resolve; }));
  const user = userEvent.setup();

  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={['/trip/42']}>
        <Link to="/trip/42">Trip A</Link><Link to="/trip/43">Trip B</Link>
        <Routes><Route path="/trip/:id" element={<TripPage />} /></Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );

  expect(await screen.findByText('History 42')).toBeTruthy();
  await user.click(screen.getByRole('button', { name: 'Send edit' }));
  await user.click(screen.getByRole('link', { name: 'Trip B' }));
  expect(await screen.findByText('History 43')).toBeTruthy();
  expect(screen.getByText('3 route days')).toBeTruthy();
  currentA = { ...tripA, itinerary_json: updated };
  aUpdated = true;
  finishEdit({ message: { id: 8, trip_id: 42, role: 'assistant', content: 'A updated', created_at: '' }, updated_itinerary: updated });
  await waitFor(() => expect(updateTripItinerary).toHaveBeenCalledWith(42, updated));
  expect(screen.queryByText('A updated')).toBeNull();
  expect(screen.getByText('3 route days')).toBeTruthy();
  await user.click(screen.getByRole('link', { name: 'Trip A' }));
  expect(await screen.findByText('2 route days')).toBeTruthy();
  expect(await screen.findByText('A updated')).toBeTruthy();
  expect(screen.queryByText('History 43')).toBeNull();
  await user.click(screen.getByRole('link', { name: 'Trip B' }));
  expect(await screen.findByText('History 43')).toBeTruthy();
  expect(screen.queryByText('A updated')).toBeNull();
});

test('a failed edit after navigation does not alter the new trip', async () => {
  vi.mocked(tripApi.getById).mockImplementation((id) => Promise.resolve({
    trip: { id, itinerary_json: { days: Array.from({ length: id === 42 ? 1 : 3 }, () => ({})) } },
    messages: { items: [{ id, trip_id: id, role: 'assistant', content: `History ${id}` }] },
  } as never));
  let failEdit!: (reason: Error) => void;
  vi.mocked(messageApi.send).mockImplementation(() => new Promise((_resolve, reject) => { failEdit = reject; }));
  const user = userEvent.setup();
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={['/trip/42']}>
        <Link to="/trip/43">Trip B</Link>
        <Routes><Route path="/trip/:id" element={<TripPage />} /></Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
  expect(await screen.findByText('History 42')).toBeTruthy();
  await user.click(screen.getByRole('button', { name: 'Send edit' }));
  await user.click(screen.getByRole('link', { name: 'Trip B' }));
  expect(await screen.findByText('History 43')).toBeTruthy();
  await act(async () => { failEdit(new Error('Edit failed')); await Promise.resolve(); });
  await waitFor(() => expect(screen.getByText('3 route days')).toBeTruthy());
  expect(screen.queryByText('History 42')).toBeNull();
  expect(updateTripItinerary).not.toHaveBeenCalled();
  expect(handleApiError).not.toHaveBeenCalled();
});
