import type { AdminBusiness } from '../../businesses/model/adminBusinesses.types'
import type { AdminSponsoredPlace } from '../../sponsored-moderation/model/adminSponsoredModeration.types'
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

type AdminAnalyticsDetailsCardProps =
  | { mode: 'business'; business: AdminBusiness }
  | { mode: 'sponsoredPlace'; place: AdminSponsoredPlace }

export function AdminAnalyticsDetailsCard(props: AdminAnalyticsDetailsCardProps) {
  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-6">
      <header className="mb-4 space-y-1">
        <h2 className="text-base font-semibold">Selected target</h2>
        <p className="text-sm text-neutral-600">
          {props.mode === 'business' ? 'Business analytics' : 'Sponsored place analytics'}
        </p>
      </header>

      {props.mode === 'business' ? (
        <>
          <Row label="ID" value={String(props.business.id)} />
          <Row label="Owner ID" value={String(props.business.owner_id)} />
          <Row label="Name" value={props.business.name} />
          <div className="pt-2">
            <StatusBadge variant={props.business.is_active ? 'success' : 'neutral'}>
              {props.business.is_active ? 'Active' : 'Inactive'}
            </StatusBadge>
          </div>
        </>
      ) : (
        <>
          <Row label="ID" value={String(props.place.id)} />
          <Row label="Business ID" value={String(props.place.business_id)} />
          <Row label="Title" value={props.place.title} />
          <Row label="City" value={props.place.city} />
          <Row label="Category" value={props.place.category} />
          <div className="pt-2 flex flex-wrap gap-2">
            <StatusBadge variant={props.place.is_approved ? 'success' : 'warning'}>
              {props.place.is_approved ? 'Approved' : 'Pending'}
            </StatusBadge>
            <StatusBadge variant={props.place.is_active ? 'success' : 'neutral'}>
              {props.place.is_active ? 'Active' : 'Inactive'}
            </StatusBadge>
          </div>
        </>
      )}
    </section>
  )
}
