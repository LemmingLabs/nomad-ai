import gsap from 'gsap';
import { TextPlugin } from 'gsap/TextPlugin';
import { type FormEvent, type ReactNode, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../../entities/message';
import styles from './ChatPanel.module.scss';

gsap.registerPlugin(TextPlugin);

const typewriterPhrases = [
  'Scenic and relaxing trip with nature and local food...',
  '5-day adventure with horse riding and nomad culture...',
  'Family-friendly tour around Issyk-Kul with comfort...',
  'Photography route through Tian Shan with iconic views...',
  '3-day mountain trekking with light outdoor activities...',
  'Explore lakes without long drives or difficult hiking...',
  'Cultural trip with masterclasses and traditional music...',
];

const getTypingDuration = (phrase: string) =>
  Math.max(0.8, phrase.length * 0.035);
const getErasingDuration = (phrase: string) =>
  Math.max(0.4, phrase.length * 0.012);

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
  const emptyRef = useRef<HTMLDivElement>(null);
  const typewriterTextRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    const typewriterText = typewriterTextRef.current;
    const emptyState = emptyRef.current;

    if (!typewriterText || !emptyState || messages.length > 0) return undefined;

    const ctx = gsap.context(() => {
      const timeline = gsap.timeline({ repeat: -1, repeatDelay: 0.1 });

      typewriterPhrases.forEach((phrase) => {
        timeline
          .set(typewriterText, { text: '' })
          .to(typewriterText, {
            duration: getTypingDuration(phrase),
            text: { value: phrase },
            ease: 'none',
          })
          .to(typewriterText, { duration: 1.5 })
          .to(typewriterText, {
            duration: getErasingDuration(phrase),
            text: { value: '' },
            ease: 'none',
          })
          .to(typewriterText, { duration: 0.15 });
      });
    }, emptyState);

    return () => ctx.revert();
  }, [messages.length]);

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
          <div ref={emptyRef} className={styles.empty}>
            <p className={styles.typewriter} aria-live='polite'>
              <span ref={typewriterTextRef} />
              <span className={styles.cursor} aria-hidden='true'>
                |
              </span>
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`${styles.message} ${styles[`message--${msg.role}`]}`}
          >
            <div className={styles.bubble}>
              {msg.role === 'assistant' ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content}
                </ReactMarkdown>
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
                <span />
                <span />
                <span />
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
            isDisabled
              ? 'Sign in to continue this conversation...'
              : 'Tell me where you want to go...'
          }
          rows={1}
          onKeyDown={handleKeyDown}
          disabled={isLoading || isDisabled}
        />
        <button
          type='submit'
          className={styles.sendBtn}
          disabled={isLoading || isDisabled}
        >
          <svg
            width='18'
            height='18'
            viewBox='0 0 24 24'
            fill='none'
            stroke='currentColor'
            strokeWidth='2.5'
            strokeLinecap='round'
            strokeLinejoin='round'
          >
            <line x1='22' y1='2' x2='11' y2='13' />
            <polygon points='22 2 15 22 11 13 2 9 22 2' />
          </svg>
        </button>
      </form>
      {disabledMessage && (
        <div style={{ padding: '0 1.5rem 1rem' }}>{disabledMessage}</div>
      )}
    </div>
  );
}
