import {
  type CSSProperties,
  type PointerEvent as ReactPointerEvent,
  type ReactNode,
  useEffect,
  useRef,
  useState,
} from 'react';
import cn from 'classnames';
import { useMediaQuery } from '../../shared/hooks';
import styles from './ResizableLayout.module.scss';

interface ResizableLayoutProps {
  left: ReactNode;
  right: ReactNode;
  isRightExpanded?: boolean;
  defaultRightWidth?: number;
  minLeftWidth?: number;
  minRightWidth?: number;
}

export function ResizableLayout({
  left,
  right,
  isRightExpanded = false,
  defaultRightWidth = 680,
  minLeftWidth = 360,
  minRightWidth = 460,
}: ResizableLayoutProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [rightWidth, setRightWidth] = useState(defaultRightWidth);
  const [isDragging, setIsDragging] = useState(false);
  const [mobilePane, setMobilePane] = useState<'itinerary' | 'chat'>('itinerary');
  const isMobile = useMediaQuery('(max-width: 767px)');

  useEffect(() => {
    if (!isDragging) {
      return undefined;
    }

    const handlePointerMove = (event: PointerEvent) => {
      const container = containerRef.current;
      if (!container) {
        return;
      }

      const bounds = container.getBoundingClientRect();
      const nextRightWidth = bounds.right - event.clientX;
      const maxRightWidth = Math.max(minRightWidth, bounds.width - minLeftWidth);

      setRightWidth(Math.min(Math.max(nextRightWidth, minRightWidth), maxRightWidth));
    };

    const handlePointerUp = () => {
      setIsDragging(false);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };

    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', handlePointerUp);

    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', handlePointerUp);
    };
  }, [isDragging, minLeftWidth, minRightWidth]);

  const handlePointerDown = (event: ReactPointerEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setIsDragging(true);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  };

  const layoutStyle: CSSProperties = isRightExpanded
    ? {}
    : {
        ['--preview-width' as string]: `${rightWidth}px`,
      };

  return (
    <div
      ref={containerRef}
      className={cn(styles.layout, {
        [styles['layout--expanded']]: isRightExpanded,
        [styles['layout--dragging']]: isDragging,
      })}
      data-print-layout="true"
      data-mobile-pane={mobilePane}
      style={layoutStyle}
    >
      <div className={styles.mobileSwitch} role="group" aria-label="Trip workspace view" data-print-hide="true">
        <button type="button" aria-pressed={mobilePane === 'itinerary'} onClick={() => setMobilePane('itinerary')}>Itinerary</button>
        <button type="button" aria-pressed={mobilePane === 'chat'} onClick={() => setMobilePane('chat')}>Chat</button>
      </div>
      <section className={styles.left} data-print-hide="true" aria-hidden={isMobile && mobilePane !== 'chat'} inert={isMobile && mobilePane !== 'chat'}>{left}</section>
      <button
        type="button"
        className={styles.handle}
        data-print-hide="true"
        onPointerDown={handlePointerDown}
        aria-label="Resize trip preview"
      >
        <span className={styles.handleGrip} />
      </button>
      <section className={styles.right} data-print-layout="true" aria-hidden={isMobile && mobilePane !== 'itinerary'} inert={isMobile && mobilePane !== 'itinerary'}>{right}</section>
    </div>
  );
}
