import type { AdminSponsoredPlaceDetails } from '../model/adminSponsoredModeration.types'
import { AdminSponsoredPlaceActions } from './AdminSponsoredPlaceActions'
import { formatDateTime } from '../../../../shared/lib/formatDateTime'
import { StatusBadge } from '../../../../shared/ui/StatusBadge'

type RowProps = {
  label: string
  value: string
}

function Row({ label, value }: RowProps) {
  return (
    <div className="grid grid-cols-3 gap-3 py-2 text-sm">
      <div className="text-neutral-500">{label}</div>
      <div className="col-span-2 text-neutral-900">{value}</div>
    </div>
  )
}

type AdminSponsoredPlaceDetailsCardProps = {
  place: AdminSponsoredPlaceDetails
}

export function AdminSponsoredPlaceDetailsCard({
  place,
}: AdminSponsoredPlaceDetailsCardProps) {
  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-6">
      <header className="mb-4 space-y-2">
        <div>
          <h2 className="text-base font-semibold">Sponsored place details</h2>
          <div className="mt-1 text-sm text-neutral-700">{place.title}</div>
        </div>

        <div className="flex flex-wrap gap-2">
          <StatusBadge variant={place.is_approved ? 'success' : 'warning'}>
            {place.is_approved ? 'Approved' : 'Pending'}
          </StatusBadge>
          <StatusBadge variant={place.is_active ? 'success' : 'neutral'}>
            {place.is_active ? 'Active' : 'Inactive'}
          </StatusBadge>
        </div>

        <div className="pt-2">
          <AdminSponsoredPlaceActions place={place} />
        </div>
      </header>

      <Row label="ID" value={String(place.id)} />
      <Row label="Business ID" value={String(place.business_id)} />
      <Row label="City" value={place.city} />
      <Row label="Category" value={place.category} />
      <Row label="Address" value={place.address} />
      <Row label="Lat" value={String(place.lat)} />
      <Row label="Lng" value={String(place.lng)} />
      <Row label="Phone" value={place.contact_phone ?? '—'} />
      <Row label="Website" value={place.website_url ?? '—'} />
      <Row label="CTA text" value={place.cta_text ?? '—'} />
      <Row label="Created" value={formatDateTime(place.created_at)} />

      <div className="pt-2">
        <div className="text-sm text-neutral-500">Description</div>
        <div className="mt-1 whitespace-pre-wrap text-sm text-neutral-900">
          {place.description}
        </div>
      </div>
    </section>
  )
}
