import { useEffect, useRef } from 'react';

/**
 * Run a callback on clicks outside the given element ref.
 */
export function useClickOutside<T extends HTMLElement>(
  callback: () => void,
) {
  const ref = useRef<T>(null);

  useEffect(() => {
    const handler = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        callback();
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [callback]);

  return ref;
}
