import axios from 'axios'

type ErrorPayload = {
  detail?: unknown
  message?: unknown
  error?: unknown
}

function getPayloadMessage(payload: unknown): string | null {
  if (!payload) return null
  if (typeof payload === 'string') return payload
  if (typeof payload !== 'object') return null

  const data = payload as ErrorPayload
  if (typeof data.detail === 'string' && data.detail.trim() !== '') return data.detail
  if (typeof data.message === 'string' && data.message.trim() !== '') return data.message
  if (typeof data.error === 'string' && data.error.trim() !== '') return data.error

  return null
}

export function getErrorMessage(error: unknown, fallback = 'Something went wrong') {
  if (axios.isAxiosError(error)) {
    const payloadMessage = getPayloadMessage(error.response?.data)
    if (payloadMessage) return payloadMessage
    if (typeof error.message === 'string' && error.message.trim() !== '') return error.message
    return fallback
  }

  if (error instanceof Error && typeof error.message === 'string') {
    return error.message || fallback
  }

  if (typeof error === 'string' && error.trim() !== '') return error

  return fallback
}

