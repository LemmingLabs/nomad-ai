import gsap from 'gsap';
import { TextPlugin } from 'gsap/TextPlugin';
import { type FormEvent, type ReactNode, useEffect, useLayoutEffect, useRef, useState } from 'react';
import type { Message } from '../../entities/message';
import type { TripItinerary } from '../../entities/trip';
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
  itinerary?: TripItinerary | null;
  onSend: (content: string) => void;
  hasOlder?: boolean;
  isLoadingOlder?: boolean;
  olderError?: boolean;
  onLoadOlder?: () => void;
}

function getRefinementSuggestions(itinerary?: TripItinerary | null) {
  const hasLongTransfer = itinerary?.days.some(
    (day) => (day.route_from_previous?.duration_mins ?? 0) >= 120,
  );
  const firstInterest = itinerary?.interests?.[0];

  return [
    {
      label: 'Slow the pace',
      prompt: 'Make this itinerary more relaxed, with fewer activities each day and more time for breaks.',
    },
    hasLongTransfer
      ? {
          label: 'Shorten long transfers',
          prompt: 'Look for ways to reduce the longest transfers in this itinerary, and clearly note any route details that are only suggestions.',
        }
      : {
          label: 'Add local food and culture',
          prompt: 'Add a few more local food and cultural experiences that fit this itinerary.',
        },
    firstInterest
      ? {
          label: `More ${firstInterest}`,
          prompt: `Add more ${firstInterest} experiences while keeping the trip length and overall pace similar.`,
        }
      : {
          label: 'Add more nature',
          prompt: 'Add a few more nature-focused stops that fit this itinerary.',
        },
  ];
}

export function ChatPanel({
  messages,
  isLoading = false,
  isDisabled = false,
  disabledMessage,
  disabledPlaceholder = 'Sign in to continue this conversation...',
  notice,
  itinerary,
  onSend,
  hasOlder = false,
  isLoadingOlder = false,
  olderError = false,
  onLoadOlder,
}: ChatPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const lastIdsRef = useRef<number[]>([]);
  const scrollSnapshotRef = useRef({ height: 0, top: 0 });
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const emptyRef = useRef<HTMLDivElement>(null);
  const typewriterTextRef = useRef<HTMLSpanElement>(null);
  const hasHydratedAssistantHistoryRef = useRef(false);
  const seenAssistantIdsRef = useRef<Set<number>>(new Set());
  const seenMessageIdsRef = useRef<Set<number>>(new Set());
  const [animatingAssistantIds, setAnimatingAssistantIds] = useState<number[]>([]);

  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    bottomRef.current?.scrollIntoView({ behavior });
  };

  useLayoutEffect(() => {
    const previous = lastIdsRef.current;
    const current = messages.map((message) => message.id);
    const previousFirstIndex = previous.length ? current.indexOf(previous[0]) : -1;
    const previousLastIndex = previous.length ? current.indexOf(previous[previous.length - 1]) : -1;
    const prepended = previousFirstIndex > 0;
    const appended = previousLastIndex >= 0 && previousLastIndex < current.length - 1;
    if (prepended && scrollRef.current && !appended) {
      scrollRef.current.scrollTop = scrollSnapshotRef.current.top + scrollRef.current.scrollHeight - scrollSnapshotRef.current.height;
    } else if (!previous.length || appended) {
      scrollToBottom(previous.length ? 'smooth' : 'auto');
    }
    lastIdsRef.current = current;
    const scrollElement = scrollRef.current;
    return () => {
      if (scrollElement) scrollSnapshotRef.current = { height: scrollElement.scrollHeight, top: scrollElement.scrollTop };
    };
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
      messages.forEach((message) => seenMessageIdsRef.current.add(message.id));
      hasHydratedAssistantHistoryRef.current = true;
      return;
    }

    const lastSeenIndex = messages.reduce((last, message, index) => seenMessageIdsRef.current.has(message.id) ? index : last, -1);
    const newAssistantIds = assistantMessages
      .filter((message) => !seenAssistantIdsRef.current.has(message.id) && messages.indexOf(message) > lastSeenIndex)
      .map((message) => message.id);

    assistantMessages.forEach((message) => seenAssistantIdsRef.current.add(message.id));
    messages.forEach((message) => seenMessageIdsRef.current.add(message.id));

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

  const submitMessage = () => {
    const val = inputRef.current?.value.trim();
    if (!val || isLoading || isDisabled) return;
    onSend(val);
    if (inputRef.current) inputRef.current.value = '';
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    submitMessage();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitMessage();
    }
  };

  return (
    <div className={styles.panel}>
      {/* Messages */}
      <div className={styles.messages} ref={scrollRef}>
        {hasOlder && <button type="button" className={styles.refinementButton} onClick={onLoadOlder} disabled={isLoadingOlder}>
          {isLoadingOlder ? 'Loading older messages…' : olderError ? 'Retry loading older messages' : 'Load older messages'}
        </button>}
        {olderError && <p role="alert">Could not load older messages. Please try again.</p>}
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
        <div className={styles.refinements} role="group" aria-label="Quick trip refinements">
          <p className={styles.refinementLabel}>Try a quick edit</p>
          <div className={styles.refinementList}>
            {getRefinementSuggestions(itinerary).map((suggestion) => (
              <button
                key={suggestion.label}
                type="button"
                className={styles.refinementButton}
                onClick={() => onSend(suggestion.prompt)}
                disabled={isLoading || isDisabled}
              >
                {suggestion.label}
              </button>
            ))}
          </div>
        </div>
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
