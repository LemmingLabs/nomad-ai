export type Id = string

export type ApiErrorResponse = {
  message?: string
  detail?: string
  code?: string
}

export type PaginatedResponse<T> = {
  items: T[]
  total: number
  page: number
  pageSize: number
}

