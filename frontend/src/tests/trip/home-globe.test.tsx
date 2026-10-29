import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HomeGlobe } from '../../widgets/home-globe';

vi.mock('../../shared/hooks', () => ({ useMediaQuery: () => true }));

afterEach(cleanup);

test('keeps a landscape available as inspiration when its destination is disabled', async () => {
  const user = userEvent.setup();
  const onPlan = vi.fn();

  render(<HomeGlobe destinations={[{
    id: 'kg', country_code: 'KG', country_name: 'Kyrgyzstan', name: 'Kyrgyzstan', enabled: false,
  }]} onPlan={onPlan}><p>Trip planning</p></HomeGlobe>);

  await user.click(screen.getByRole('button', { name: /explore the globe/i }));
  await user.click(screen.getByRole('button', { name: /issyk-kul/i }));
  expect(screen.getByRole('heading', { name: 'Issyk-Kul' })).toBeTruthy();
  expect(screen.queryByRole('button', { name: /plan kyrgyzstan/i })).toBeNull();
  expect(onPlan).not.toHaveBeenCalled();
});
