import type { AdminAnalyticsMode } from '../model/adminAnalytics.types'

const modes: { value: AdminAnalyticsMode; label: string }[] = [
  { value: 'business', label: 'Businesses' },
  { value: 'sponsoredPlace', label: 'Sponsored places' },
]

type AdminAnalyticsModeSwitcherProps = {
  value: AdminAnalyticsMode
  onChange: (mode: AdminAnalyticsMode) => void
}

export function AdminAnalyticsModeSwitcher({
  value,
  onChange,
}: AdminAnalyticsModeSwitcherProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {modes.map((m) => {
        const isActive = value === m.value
        return (
          <button
            key={m.value}
            type="button"
            onClick={() => onChange(m.value)}
            className={[
              'rounded-md border px-3 py-1.5 text-sm font-medium',
              isActive
                ? 'border-neutral-900 bg-neutral-900 text-white'
                : 'border-neutral-200 bg-white text-neutral-900 hover:bg-neutral-50',
            ].join(' ')}
          >
            {m.label}
          </button>
        )
      })}
    </div>
  )
}

