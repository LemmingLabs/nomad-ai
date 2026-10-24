import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { TripPage } from '../../pages/trip/TripPage';
import { tripApi } from '../../entities/trip';
import { messageApi } from '../../entities/message';

const setActiveTrip = vi.fn();
const updateTrip = vi.fn();
const setCollapsed = vi.fn();

vi.mock('../../entities/trip', () => ({
  tripApi: { getById: vi.fn() },
  useTripStore: () => ({ trips: [], setActiveTrip, updateTrip }),
}));
vi.mock('../../entities/message', () => ({ messageApi: { send: vi.fn() } }));
vi.mock('../../entities/user', () => ({ useUserStore: () => ({ isAuthenticated: true }) }));
vi.mock('../../entities/limit', () => ({
  useMyLimitsQuery: () => ({ data: { chat_edits_used: 0, chat_edit_limit_per_day: 5 } }),
  limitQueryKeys: { me: () => ['limits', 'me'] },
}));
vi.mock('../../features/ui/open-sidebar', () => ({
  useSidebarStore: () => ({ isOpen: true, isCollapsed: false, setCollapsed }),
}));
vi.mock('../../shared/hooks', () => ({ useMediaQuery: () => false }));
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
  expect(updateTrip).toHaveBeenCalledWith(expect.objectContaining({ itinerary_json: updatedItinerary }));
  await user.click(screen.getByRole('button', { name: 'Focus route' }));
  await waitFor(() => expect(setCollapsed).toHaveBeenCalledWith(true));
});
