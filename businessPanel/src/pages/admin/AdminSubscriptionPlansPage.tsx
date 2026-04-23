import { useMemo, useState } from 'react'

import type {
  SubscriptionPlan,
  SubscriptionPlanFormValues,
} from '../../features/admin/subscription-plans/model/adminSubscriptionPlans.types'
import {
  useActivateAdminSubscriptionPlanMutation,
  useAdminSubscriptionPlansQuery,
  useCreateAdminSubscriptionPlanMutation,
  useDeactivateAdminSubscriptionPlanMutation,
  useUpdateAdminSubscriptionPlanMutation,
} from '../../features/admin/subscription-plans/model/adminSubscriptionPlans.hooks'
import {
  mapFormValuesToCreatePayload,
  mapFormValuesToUpdatePayload,
  mapPlanToFormValues,
} from '../../features/admin/subscription-plans/model/adminSubscriptionPlans.utils'
import { AdminSubscriptionPlanForm } from '../../features/admin/subscription-plans/ui/AdminSubscriptionPlanForm'
import { AdminSubscriptionPlanModal } from '../../features/admin/subscription-plans/ui/AdminSubscriptionPlanModal'
import { AdminSubscriptionPlansEmptyState } from '../../features/admin/subscription-plans/ui/AdminSubscriptionPlansEmptyState'
import { AdminSubscriptionPlansTable } from '../../features/admin/subscription-plans/ui/AdminSubscriptionPlansTable'
import { confirmAction } from '../../shared/lib/confirm'
import { getErrorMessage } from '../../shared/lib/getErrorMessage'
import { PageErrorState } from '../../shared/ui/PageErrorState'
import { PageLoadingState } from '../../shared/ui/PageLoadingState'

const emptyValues: SubscriptionPlanFormValues = {
  name: '',
  price: 0,
  currency: 'USD',
  billing_period: 'monthly',
  trip_limit_per_day: 0,
  chat_edit_limit_per_day: 0,
  is_active: true,
}

export function AdminSubscriptionPlansPage() {
  const plansQuery = useAdminSubscriptionPlansQuery()
  const createMutation = useCreateAdminSubscriptionPlanMutation()
  const updateMutation = useUpdateAdminSubscriptionPlanMutation()
  const activateMutation = useActivateAdminSubscriptionPlanMutation()
  const deactivateMutation = useDeactivateAdminSubscriptionPlanMutation()

  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<SubscriptionPlan | null>(null)
  const [togglingId, setTogglingId] = useState<number | null>(null)

  const openCreate = () => {
    setEditing(null)
    setOpen(true)
  }

  const openEdit = (plan: SubscriptionPlan) => {
    setEditing(plan)
    setOpen(true)
  }

  const close = () => {
    setOpen(false)
    setEditing(null)
  }

  const initialValues = useMemo(() => {
    if (!editing) return emptyValues
    return mapPlanToFormValues(editing)
  }, [editing])

  if (plansQuery.isLoading) {
    return <PageLoadingState message="Loading subscription plans..." />
  }

  if (plansQuery.isError) {
    return (
      <PageErrorState
        title="Subscription plans"
        message={getErrorMessage(plansQuery.error, 'Failed to load subscription plans')}
        onRetry={() => plansQuery.refetch()}
      />
    )
  }

  const plans = plansQuery.data ?? []

  const isSubmitting = createMutation.isPending || updateMutation.isPending
  const formErrorMessage =
    createMutation.isError || updateMutation.isError
      ? getErrorMessage(
          (createMutation.error ?? updateMutation.error) as unknown,
          'Failed to save subscription plan',
        )
      : null

  const handleToggleActive = async (plan: SubscriptionPlan) => {
    const ok = confirmAction({
      title: plan.is_active ? 'Deactivate this plan?' : 'Activate this plan?',
      description: plan.is_active
        ? 'Inactive plans are not shown to users in public flows.'
        : 'This plan will become available for users in public flows.',
    })
    if (!ok) return

    setTogglingId(plan.id)
    try {
      if (plan.is_active) {
        await deactivateMutation.mutateAsync(plan.id)
      } else {
        await activateMutation.mutateAsync(plan.id)
      }
    } finally {
      setTogglingId(null)
    }
  }

  return (
    <div className="space-y-6">
      <header className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-lg font-semibold">Subscription plans</h1>
          <p className="text-sm text-neutral-600">
            Plans control pricing and user limits (trip and chat edit limits).
          </p>
        </div>
        <button
          type="button"
          onClick={openCreate}
          className="shrink-0 rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800"
        >
          Create plan
        </button>
      </header>

      {plans.length === 0 ? (
        <AdminSubscriptionPlansEmptyState onCreate={openCreate} />
      ) : (
        <AdminSubscriptionPlansTable
          plans={plans}
          onEdit={openEdit}
          onToggleActive={handleToggleActive}
          togglingId={togglingId}
        />
      )}

      {activateMutation.isError || deactivateMutation.isError ? (
        <p className="text-sm text-red-600">
          {getErrorMessage(
            (activateMutation.error ?? deactivateMutation.error) as unknown,
            'Failed to update plan status',
          )}
        </p>
      ) : null}

      <AdminSubscriptionPlanModal
        open={open}
        title={editing ? `Edit plan: ${editing.name}` : 'Create subscription plan'}
        onClose={close}
      >
        <AdminSubscriptionPlanForm
          initialValues={initialValues}
          submitLabel={editing ? 'Save changes' : 'Create'}
          isSubmitting={isSubmitting}
          errorMessage={formErrorMessage}
          onCancel={close}
          onSubmit={async (values) => {
            if (editing) {
              await updateMutation.mutateAsync({
                planId: editing.id,
                payload: mapFormValuesToUpdatePayload(values),
              })
              close()
              return
            }

            await createMutation.mutateAsync(mapFormValuesToCreatePayload(values))
            close()
          }}
        />
      </AdminSubscriptionPlanModal>
    </div>
  )
}

