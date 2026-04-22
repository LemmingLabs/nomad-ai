import { useEffect, useMemo, useState } from 'react';
import gsap from 'gsap';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../../entities/message';
import styles from './ChatPanel.module.scss';

interface AnimatedAssistantMessageProps {
  message: Message;
  shouldAnimate: boolean;
  onAnimationComplete: (messageId: number) => void;
  onRevealProgress: () => void;
}

function buildRevealSteps(content: string): string[] {
  const tokens = content.match(/\S+\s*|\n+/g) ?? [content];
  const steps: string[] = [];
  let currentChunk = '';
  let visibleTokens = 0;

  tokens.forEach((token) => {
    currentChunk += token;

    if (token.trim().length > 0) {
      visibleTokens += 1;
    }

    if (visibleTokens >= 2 || token.includes('\n')) {
      steps.push(currentChunk);
      currentChunk = '';
      visibleTokens = 0;
    }
  });

  if (currentChunk) {
    steps.push(currentChunk);
  }

  return steps.length > 0 ? steps : [content];
}

function getRevealDuration(stepCount: number): number {
  return Math.min(4.8, Math.max(1.2, stepCount * 0.085));
}

export function AnimatedAssistantMessage({
  message,
  shouldAnimate,
  onAnimationComplete,
  onRevealProgress,
}: AnimatedAssistantMessageProps) {
  const revealSteps = useMemo(() => buildRevealSteps(message.content), [message.content]);
  const [visibleContent, setVisibleContent] = useState(
    shouldAnimate ? '' : message.content,
  );
  const [isAnimationDone, setIsAnimationDone] = useState(!shouldAnimate);

  useEffect(() => {
    if (!shouldAnimate) {
      return undefined;
    }

    const progress = { step: 0 };
    const tween = gsap.to(progress, {
      step: revealSteps.length,
      duration: getRevealDuration(revealSteps.length),
      ease: 'none',
      snap: { step: 1 },
      onUpdate: () => {
        const currentStep = Math.min(revealSteps.length, Math.floor(progress.step));
        const nextContent =
          currentStep > 0 ? revealSteps.slice(0, currentStep).join('') : '';

        setVisibleContent(nextContent);
        onRevealProgress();
      },
      onComplete: () => {
        setVisibleContent(message.content);
        setIsAnimationDone(true);
        onRevealProgress();
        onAnimationComplete(message.id);
      },
    });

    return () => {
      tween.kill();
    };
  }, [
    message.content,
    message.id,
    onAnimationComplete,
    onRevealProgress,
    revealSteps,
    shouldAnimate,
  ]);

  if (!isAnimationDone) {
    return (
      <div className={styles.animatedText} aria-live='polite'>
        <span>{visibleContent}</span>
        <span className={styles.cursor} aria-hidden='true'>
          |
        </span>
      </div>
    );
  }

  return <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>;
}
