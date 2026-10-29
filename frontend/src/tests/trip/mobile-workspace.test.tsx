import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ResizableLayout } from '../../widgets/resizable-layout';

vi.mock('../../shared/hooks', () => ({ useMediaQuery: () => true }));
afterEach(cleanup);

test('switches between itinerary and chat without losing a draft', async () => {
  const user = userEvent.setup();
  const print = vi.fn();
  render(<ResizableLayout
    left={<label>Message<textarea /></label>}
    right={<div><h2>Day one</h2><button onClick={print}>Print itinerary</button></div>}
  />);

  expect(screen.getByRole('button', { name: 'Itinerary' }).getAttribute('aria-pressed')).toBe('true');
  expect(screen.getByRole('heading', { name: 'Day one' })).toBeTruthy();
  await user.click(screen.getByRole('button', { name: 'Print itinerary' }));
  expect(print).toHaveBeenCalledOnce();
  await user.click(screen.getByRole('button', { name: 'Chat' }));
  expect(screen.queryByRole('heading', { name: 'Day one' })).toBeNull();
  await user.type(screen.getByRole('textbox', { name: 'Message' }), 'A draft edit');
  await user.click(screen.getByRole('button', { name: 'Itinerary' }));
  await user.click(screen.getByRole('button', { name: 'Chat' }));
  expect(screen.getByRole('textbox', { name: 'Message' })).toHaveProperty('value', 'A draft edit');
});
