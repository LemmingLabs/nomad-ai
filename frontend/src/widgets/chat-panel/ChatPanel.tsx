import gsap from 'gsap';
import { TextPlugin } from 'gsap/TextPlugin';
import { type FormEvent, type ReactNode, useEffect, useRef, useState } from 'react';
import type { Message } from '../../entities/message';
import { AnimatedAssistantMessage } from './AnimatedAssistantMessage';
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
  disabledPlaceholder?: string;
  notice?: ReactNode;
  onSend: (content: string) => void;
}

export function ChatPanel({
  messages,
  isLoading = false,
  isDisabled = false,
  disabledMessage,
  disabledPlaceholder = 'Sign in to continue this conversation...',
  notice,
  onSend,
}: ChatPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const emptyRef = useRef<HTMLDivElement>(null);
  const typewriterTextRef = useRef<HTMLSpanElement>(null);
  const hasHydratedAssistantHistoryRef = useRef(false);
  const seenAssistantIdsRef = useRef<Set<number>>(new Set());
  const [animatingAssistantIds, setAnimatingAssistantIds] = useState<number[]>([]);

  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    bottomRef.current?.scrollIntoView({ behavior });
  };

  useEffect(() => {
    scrollToBottom(messages.length > 0 ? 'smooth' : 'auto');
  }, [messages]);

  useEffect(() => {
    const assistantMessages = messages.filter((message) => message.role === 'assistant');

    if (!hasHydratedAssistantHistoryRef.current) {
      if (messages.length === 0) {
        return;
      }

      assistantMessages.forEach((message) => {
        seenAssistantIdsRef.current.add(message.id);
      });
      hasHydratedAssistantHistoryRef.current = true;
      return;
    }

    const newAssistantIds = assistantMessages
      .filter((message) => !seenAssistantIdsRef.current.has(message.id))
      .map((message) => message.id);

    if (newAssistantIds.length === 0) {
      return;
    }

    newAssistantIds.forEach((messageId) => {
      seenAssistantIdsRef.current.add(messageId);
    });
    setAnimatingAssistantIds((currentIds) => [...currentIds, ...newAssistantIds]);
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
                <AnimatedAssistantMessage
                  message={msg}
                  shouldAnimate={animatingAssistantIds.includes(msg.id)}
                  onRevealProgress={() => scrollToBottom('auto')}
                  onAnimationComplete={(messageId) => {
                    setAnimatingAssistantIds((currentIds) =>
                      currentIds.filter((id) => id !== messageId),
                    );
                  }}
                />
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
      {notice}
      <form className={styles.form} onSubmit={handleSubmit}>
        <textarea
          ref={inputRef}
          className={styles.input}
          placeholder={
            isDisabled
              ? disabledPlaceholder
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
