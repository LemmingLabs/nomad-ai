import { PageEmptyState } from '../../../../shared/ui/PageEmptyState'

type AdminSubscriptionPlansEmptyStateProps = {
  onCreate: () => void
}

export function AdminSubscriptionPlansEmptyState({ onCreate }: AdminSubscriptionPlansEmptyStateProps) {
  return (
    <PageEmptyState
      title="No subscription plans yet"
      description="Create the first plan to control pricing and user limits."
      action={
        <button
          type="button"
          onClick={onCreate}
          className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800"
        >
          Create plan
        </button>
      }
    />
  )
}

