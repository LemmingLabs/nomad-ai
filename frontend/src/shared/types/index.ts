// ─── Shared TypeScript Types ─────────────────────────────────────────────────

export interface ApiError {
  message: string;
  status?: number;
  detail?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

export type Nullable<T> = T | null;

export type Optional<T> = T | undefined;

export type ID = string | number;
