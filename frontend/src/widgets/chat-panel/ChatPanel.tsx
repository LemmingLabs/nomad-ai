import { type FormEvent, type ReactNode, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../../entities/message';
import styles from './ChatPanel.module.scss';

interface ChatPanelProps {
  messages: Message[];
  isLoading?: boolean;
  isDisabled?: boolean;
  disabledMessage?: ReactNode;
  onSend: (content: string) => void;
}

export function ChatPanel({
  messages,
  isLoading = false,
  isDisabled = false,
  disabledMessage,
  onSend,
}: ChatPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const val = inputRef.current?.value.trim();
    if (!val || isLoading || isDisabled) return;
    onSend(val);
    if (inputRef.current) inputRef.current.value = '';
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  };

  return (
    <div className={styles.panel}>
      {/* Messages */}
      <div className={styles.messages}>
        {messages.length === 0 && (
          <div className={styles.empty}>
            <p>Ask AI to plan your perfect trip ✈️</p>
          </div>
        )}
        {messages.map((msg) => (
          <div key={msg.id} className={`${styles.message} ${styles[`message--${msg.role}`]}`}>
            <div className={styles.bubble}>
              {msg.role === 'assistant' ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
              ) : (
                <p>{msg.content}</p>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className={`${styles.message} ${styles['message--assistant']}`}>
            <div className={styles.bubble}>
              <span className={styles.typing}>
                <span /><span /><span />
              </span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form className={styles.form} onSubmit={handleSubmit}>
        <textarea
          ref={inputRef}
          className={styles.input}
          placeholder={
            isDisabled ? 'Sign in to continue this conversation...' : 'Tell me where you want to go...'
          }
          rows={1}
          onKeyDown={handleKeyDown}
          disabled={isLoading || isDisabled}
        />
        <button type="submit" className={styles.sendBtn} disabled={isLoading || isDisabled}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </form>
      {disabledMessage && <div style={{ padding: '0 1.5rem 1rem' }}>{disabledMessage}</div>}
    </div>
  );
}
