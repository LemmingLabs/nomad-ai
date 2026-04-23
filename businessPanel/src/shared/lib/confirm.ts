export type ConfirmActionOptions = {
  title: string
  description?: string
}

export function confirmAction({ title, description }: ConfirmActionOptions) {
  if (typeof window === 'undefined') return false
  const text = description ? `${title}\n\n${description}` : title
  return window.confirm(text)
}

