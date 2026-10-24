import { afterEach, beforeAll, expect, test, vi } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatPanel } from '../../widgets/chat-panel/ChatPanel';

afterEach(cleanup);
beforeAll(() => {
  HTMLElement.prototype.scrollIntoView = vi.fn();
});

const history = [{
  id: 1, trip_id: 42, role: 'user' as const,
  content: 'Plan a lake trip', created_at: '2026-01-01T10:00:00Z',
}];

test('sends a trimmed edit on Enter and keeps Shift+Enter for multiline input', async () => {
  const send = vi.fn();
  const user = userEvent.setup();
  render(<ChatPanel messages={history} onSend={send} />);
  const input = screen.getByPlaceholderText('Tell me where you want to go...');

  await user.type(input, '  Add a lake stop  {Shift>}{Enter}{/Shift}');
  expect(send).not.toHaveBeenCalled();
  await user.keyboard('{Enter}');
  expect(send).toHaveBeenCalledWith('Add a lake stop');
  expect(input).toHaveProperty('value', '');
});

test('blocks edits when the chat is disabled', async () => {
  const send = vi.fn();
  render(<ChatPanel
    messages={history}
    onSend={send}
    isDisabled
    disabledPlaceholder="Sign in to continue"
    disabledMessage="Sign in first"
  />);
  const input = screen.getByPlaceholderText('Sign in to continue');
  expect(input.hasAttribute('disabled')).toBe(true);
  expect(screen.getByText('Sign in first')).toBeTruthy();
  await userEvent.setup().keyboard('{Enter}');
  expect(send).not.toHaveBeenCalled();
});
