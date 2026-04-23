import { StatusBadge } from '../../../../shared/ui/StatusBadge'

type AdminSubscriptionPlanStatusBadgeProps = {
  isActive: boolean
}

export function AdminSubscriptionPlanStatusBadge({
  isActive,
}: AdminSubscriptionPlanStatusBadgeProps) {
  return (
    <StatusBadge variant={isActive ? 'success' : 'neutral'}>
      {isActive ? 'Active' : 'Inactive'}
    </StatusBadge>
  )
}

