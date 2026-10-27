import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { GenerateTripForm } from '../../widgets/generate-trip-form/GenerateTripForm';

vi.mock('../../entities/limit', () => ({ useMyLimitsQuery: () => ({ data: null }) }));
vi.mock('../../entities/user', () => ({ useUserStore: () => ({ isAuthenticated: false }) }));
vi.mock('../../entities/destination', () => ({
  useDestinationsQuery: () => ({
    data: [{ id: 'kg', country_code: 'KG', country_name: 'Kyrgyzstan', name: 'Kyrgyzstan', enabled: true }],
    isLoading: false,
    isError: false,
  }),
}));

afterEach(cleanup);

test('submits the selected budget, interests, and trip brief', async () => {
  const submit = vi.fn();
  const user = userEvent.setup();
  render(<GenerateTripForm onSubmit={submit} />);

  await user.click(screen.getByRole('radio', { name: /higher comfort/i }));
  await user.click(screen.getByText(/personalize your trip/i));
  await user.click(screen.getByRole('button', { name: 'nature' }));
  await user.click(screen.getByRole('button', { name: 'culture' }));
  await user.type(screen.getByRole('textbox', { name: /add custom interest/i }), ' Stargazing ');
  await user.click(screen.getByRole('button', { name: 'Add' }));
  await user.type(screen.getByRole('textbox', { name: /prompt/i }), 'Quiet mountain roads');
  await user.click(screen.getByRole('button', { name: /generate itinerary/i }));

  await waitFor(() => expect(submit).toHaveBeenCalledOnce());
  expect(submit.mock.calls[0][0]).toMatchObject({
    budget: 'high',
    days: 5,
    interests: 'nature, culture, stargazing',
    prompt: 'Quiet mountain roads',
    country_code: 'KG',
    destination_id: 'kg',
  });
});

test('submits a general trip when optional preferences are skipped', async () => {
  const submit = vi.fn();
  const user = userEvent.setup();
  render(<GenerateTripForm onSubmit={submit} />);

  await user.click(screen.getByRole('button', { name: /generate itinerary/i }));

  await waitFor(() => expect(submit).toHaveBeenCalledOnce());
  expect(submit.mock.calls[0][0]).toMatchObject({
    interests: '',
    prompt: '',
    travel_style: 'relaxed',
  });
});
