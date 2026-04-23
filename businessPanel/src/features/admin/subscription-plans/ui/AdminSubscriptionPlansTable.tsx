import type { SubscriptionPlan } from '../model/adminSubscriptionPlans.types'
import { formatBillingPeriodLabel, formatPrice } from '../model/adminSubscriptionPlans.utils'
import { AdminSubscriptionPlanStatusBadge } from './AdminSubscriptionPlanStatusBadge'

type AdminSubscriptionPlansTableProps = {
  plans: SubscriptionPlan[]
  togglingId?: number | null
  onEdit: (plan: SubscriptionPlan) => void
  onToggleActive: (plan: SubscriptionPlan) => void
}

export function AdminSubscriptionPlansTable({
  plans,
  togglingId,
  onEdit,
  onToggleActive,
}: AdminSubscriptionPlansTableProps) {
  return (
    <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-neutral-200 bg-neutral-50 text-xs uppercase tracking-wide text-neutral-500">
          <tr>
            <th className="px-4 py-3">Name</th>
            <th className="px-4 py-3">Price</th>
            <th className="px-4 py-3">Billing</th>
            <th className="px-4 py-3">Trip limit</th>
            <th className="px-4 py-3">Chat edit limit</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {plans.map((p) => (
            <tr key={p.id} className="border-b border-neutral-200 last:border-b-0">
              <td className="px-4 py-3">
                <div className="font-medium text-neutral-900">{p.name}</div>
                <div className="text-xs text-neutral-500">ID: {p.id}</div>
              </td>
              <td className="px-4 py-3 text-neutral-700">{formatPrice(p.price, p.currency)}</td>
              <td className="px-4 py-3 text-neutral-700">
                {formatBillingPeriodLabel(p.billing_period)}
              </td>
              <td className="px-4 py-3 text-neutral-700">{p.trip_limit_per_day}</td>
              <td className="px-4 py-3 text-neutral-700">{p.chat_edit_limit_per_day}</td>
              <td className="px-4 py-3">
                <AdminSubscriptionPlanStatusBadge isActive={p.is_active} />
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => onEdit(p)}
                    className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    onClick={() => onToggleActive(p)}
                    disabled={togglingId === p.id}
                    className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {togglingId === p.id
                      ? p.is_active
                        ? 'Deactivating...'
                        : 'Activating...'
                      : p.is_active
                        ? 'Deactivate'
                        : 'Activate'}
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

