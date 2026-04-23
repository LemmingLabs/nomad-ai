import type { AdminBusinessDetails } from '../model/adminBusinesses.types'
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

type AdminBusinessDetailsCardProps = {
  business: AdminBusinessDetails
}

export function AdminBusinessDetailsCard({ business }: AdminBusinessDetailsCardProps) {
  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-6">
      <header className="mb-4">
        <h2 className="text-base font-semibold">Business details</h2>
        <div className="mt-2">
          <StatusBadge variant={business.is_active ? 'success' : 'neutral'}>
            {business.is_active ? 'Active' : 'Inactive'}
          </StatusBadge>
        </div>
      </header>

      <Row label="ID" value={String(business.id)} />
      <Row label="Owner ID" value={String(business.owner_id)} />
      <Row label="Name" value={business.name} />
      <Row label="Phone" value={business.contact_phone ?? '—'} />
      <Row label="Website" value={business.website_url ?? '—'} />
      <Row label="Created" value={formatDateTime(business.created_at)} />
      <Row label="Updated" value={formatDateTime(business.updated_at)} />

      <div className="pt-2">
        <div className="text-sm text-neutral-500">Description</div>
        <div className="mt-1 whitespace-pre-wrap text-sm text-neutral-900">
          {business.description ?? '—'}
        </div>
      </div>
    </section>
  )
}
