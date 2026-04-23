import axios from 'axios';
import type { Limits } from '../../../../entities/limit';

export const FREE_PLAN_NAME = 'FREE';

export const fallbackFreeLimits: Limits = {
  plan: FREE_PLAN_NAME,
  trip_limit_per_day: 1,
  trip_generations_used: 0,
  chat_edit_limit_per_day: 0,
  chat_edits_used: 0,
};

export function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value));
}

export function getRemaining(used: number, limit: number): number {
  if (!Number.isFinite(limit) || limit <= 0) return 0;
  return Math.max(0, limit - Math.max(0, used));
}

export function getUsageRatio(used: number, limit: number): number {
  if (!Number.isFinite(limit) || limit <= 0) {
    return used > 0 ? 1 : 0;
  }
  return clamp01(used / limit);
}

export type UsageTone = 'ok' | 'warn' | 'danger';

export function getUsageTone(used: number, limit: number): UsageTone {
  const remaining = getRemaining(used, limit);
  if (limit <= 0) return 'danger';
  if (remaining <= 0) return 'danger';
  if (remaining <= 2) return 'warn';
  return 'ok';
}

export function isLimitExceededError(error: unknown): boolean {
  if (!axios.isAxiosError(error)) return false;
  if (error.response?.status !== 403) return false;
  const data = error.response?.data as unknown;
  if (typeof data === 'string') return data.toLowerCase().includes('limit');
  if (data && typeof data === 'object') {
    const detail = (data as Record<string, unknown>).detail;
    const message = (data as Record<string, unknown>).message;
    if (typeof detail === 'string' && detail.toLowerCase().includes('limit')) return true;
    if (typeof message === 'string' && message.toLowerCase().includes('limit')) return true;
  }
  return true;
}

