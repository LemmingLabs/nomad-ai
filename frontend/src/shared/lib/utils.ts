import { AxiosError } from 'axios';
import { toast } from 'react-toastify';

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

/**
 * Extract a human-readable error message from an API error.
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const data: unknown = error.response?.data;
    if (typeof data === 'string') return data;
    if (isRecord(data) && typeof data.detail === 'string') return data.detail;
    if (isRecord(data) && typeof data.message === 'string') return data.message;
    return error.message;
  }
  if (error instanceof Error) return error.message;
  return 'Unexpected error occurred';
}

/**
 * Show a toast for an API error.
 */
export function handleApiError(error: unknown): void {
  toast.error(getErrorMessage(error));
}

/**
 * Format a date string to a locale-friendly date string.
 */
export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Clamp a number between min and max.
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/**
 * Generate a simple local unique ID (for optimistic UI, keys etc.)
 */
export function genLocalId(): string {
  return `local-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

/**
 * Deep-check if a value is empty (null, undefined, empty string, empty array, empty object)
 */
export function isEmpty(value: unknown): boolean {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim().length === 0;
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
}
