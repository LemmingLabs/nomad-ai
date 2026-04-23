import type { ReactNode } from 'react'

type AdminSubscriptionPlanModalProps = {
  open: boolean
  title: string
  children: ReactNode
  onClose: () => void
}

export function AdminSubscriptionPlanModal({
  open,
  title,
  children,
  onClose,
}: AdminSubscriptionPlanModalProps) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <button
        type="button"
        onClick={onClose}
        className="absolute inset-0 bg-black/40"
        aria-label="Close modal"
      />

      <div className="relative w-full max-w-2xl rounded-lg border border-neutral-200 bg-white shadow-lg">
        <div className="flex items-center justify-between border-b border-neutral-200 px-6 py-4">
          <h2 className="text-base font-semibold">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
          >
            Close
          </button>
        </div>

        <div className="px-6 py-6">{children}</div>
      </div>
    </div>
  )
}

