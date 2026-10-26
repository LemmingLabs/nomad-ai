import type { AdminSponsoredPlaceListFilters } from '../model/adminSponsoredModeration.types'

type Preset = AdminSponsoredPlaceListFilters['preset']

const presets: { value: Preset; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'inactive', label: 'Inactive' },
]

type AdminSponsoredModerationFiltersProps = {
  value: AdminSponsoredPlaceListFilters
  onChange: (value: AdminSponsoredPlaceListFilters) => void
}

export function AdminSponsoredModerationFilters({
  value,
  onChange,
}: AdminSponsoredModerationFiltersProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <label className="sr-only" htmlFor="moderation-country">Filter by country code</label>
      <input
        id="moderation-country"
        value={value.country_code ?? ''}
        onChange={(event) => onChange({ ...value, country_code: event.target.value.toUpperCase() || undefined })}
        placeholder="Country code (for example KG)"
        maxLength={2}
        className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm"
      />
      {presets.map((p) => {
        const isActive = value.preset === p.value
        return (
          <button
            key={p.value}
            type="button"
            onClick={() => onChange({ ...value, preset: p.value })}
            className={[
              'rounded-md border px-3 py-1.5 text-sm font-medium',
              isActive
                ? 'border-neutral-900 bg-neutral-900 text-white'
                : 'border-neutral-200 bg-white text-neutral-900 hover:bg-neutral-50',
            ].join(' ')}
          >
            {p.label}
          </button>
        )
      })}
    </div>
  )
}

