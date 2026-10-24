import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PricingPlans } from '../../widgets/pricing-plans/PricingPlans';

const purchase = vi.fn();

vi.mock('../../entities/subscription', () => ({
  useSubscriptionPlansQuery: () => ({
    isLoading: false,
    isSuccess: true,
    data: [
      { id: 2, name: 'PRO', price: 19, billing_period: 'monthly', trip_limit_per_day: 10, chat_edit_limit_per_day: 20 },
      { id: 1, name: 'FREE', price: 0, billing_period: 'monthly', trip_limit_per_day: 1, chat_edit_limit_per_day: 0 },
    ],
  }),
  useMySubscriptionQuery: () => ({ data: null }),
}));
vi.mock('../../entities/limit', () => ({ useMyLimitsQuery: () => ({ data: { plan: 'FREE' } }) }));
vi.mock('../../features/subscription/mock-purchase', () => ({
  useMockPurchase: () => ({ purchase, mutation: { isPending: false } }),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

test('sorts plans by price, marks the active plan, and selects the upgrade', async () => {
  render(<PricingPlans />);

  const names = screen.getAllByRole('heading', { level: 3 }).map((heading) => heading.textContent);
  expect(names).toEqual(['FREE', 'PRO']);
  expect(screen.getByRole('button', { name: 'Current plan' }).hasAttribute('disabled')).toBe(true);
  await userEvent.setup().click(screen.getByRole('button', { name: 'Upgrade' }));
  expect(purchase).toHaveBeenCalledWith(2);
});
