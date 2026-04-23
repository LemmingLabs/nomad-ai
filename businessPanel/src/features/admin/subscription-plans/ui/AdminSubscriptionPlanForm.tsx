import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'

import { subscriptionPlanFormSchema } from '../model/adminSubscriptionPlans.schemas'
import type { BillingPeriod, SubscriptionPlanFormValues } from '../model/adminSubscriptionPlans.types'

const billingOptions: { value: BillingPeriod; label: string }[] = [
  { value: 'free', label: 'Free' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'yearly', label: 'Yearly' },
]

type AdminSubscriptionPlanFormProps = {
  initialValues: SubscriptionPlanFormValues
  submitLabel: string
  isSubmitting?: boolean
  errorMessage?: string | null
  onSubmit: (values: SubscriptionPlanFormValues) => void | Promise<void>
  onCancel: () => void
}

export function AdminSubscriptionPlanForm({
  initialValues,
  submitLabel,
  isSubmitting,
  errorMessage,
  onSubmit,
  onCancel,
}: AdminSubscriptionPlanFormProps) {
  const form = useForm<SubscriptionPlanFormValues>({
    resolver: zodResolver(subscriptionPlanFormSchema),
    defaultValues: initialValues,
    mode: 'onSubmit',
  })

  useEffect(() => {
    form.reset(initialValues)
  }, [form, initialValues])

  const numberInput = (field: keyof SubscriptionPlanFormValues) =>
    form.register(field, { valueAsNumber: true })

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="space-y-1 sm:col-span-2">
          <label className="text-sm font-medium text-neutral-900">Name</label>
          <input
            className="w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isSubmitting}
            {...form.register('name')}
          />
          {form.formState.errors.name?.message ? (
            <p className="text-xs text-red-600">{form.formState.errors.name.message}</p>
          ) : null}
        </div>

        <div className="space-y-1">
          <label className="text-sm font-medium text-neutral-900">Price</label>
          <input
            type="number"
            step="0.01"
            min="0"
            className="w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isSubmitting}
            {...numberInput('price')}
          />
          {form.formState.errors.price?.message ? (
            <p className="text-xs text-red-600">{form.formState.errors.price.message}</p>
          ) : null}
        </div>

        <div className="space-y-1">
          <label className="text-sm font-medium text-neutral-900">Currency</label>
          <input
            className="w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isSubmitting}
            {...form.register('currency')}
          />
          {form.formState.errors.currency?.message ? (
            <p className="text-xs text-red-600">{form.formState.errors.currency.message}</p>
          ) : null}
        </div>

        <div className="space-y-1">
          <label className="text-sm font-medium text-neutral-900">Billing period</label>
          <select
            className="w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isSubmitting}
            {...form.register('billing_period')}
          >
            {billingOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          {form.formState.errors.billing_period?.message ? (
            <p className="text-xs text-red-600">
              {form.formState.errors.billing_period.message}
            </p>
          ) : null}
        </div>

        <div className="space-y-1">
          <label className="text-sm font-medium text-neutral-900">Trip limit / day</label>
          <input
            type="number"
            min="0"
            className="w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isSubmitting}
            {...numberInput('trip_limit_per_day')}
          />
          {form.formState.errors.trip_limit_per_day?.message ? (
            <p className="text-xs text-red-600">
              {form.formState.errors.trip_limit_per_day.message}
            </p>
          ) : null}
        </div>

        <div className="space-y-1">
          <label className="text-sm font-medium text-neutral-900">
            Chat edit limit / day
          </label>
          <input
            type="number"
            min="0"
            className="w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isSubmitting}
            {...numberInput('chat_edit_limit_per_day')}
          />
          {form.formState.errors.chat_edit_limit_per_day?.message ? (
            <p className="text-xs text-red-600">
              {form.formState.errors.chat_edit_limit_per_day.message}
            </p>
          ) : null}
        </div>

        <label className="flex items-center gap-2 sm:col-span-2">
          <input
            type="checkbox"
            disabled={isSubmitting}
            {...form.register('is_active')}
            className="h-4 w-4 rounded border-neutral-300"
          />
          <span className="text-sm text-neutral-900">Active</span>
        </label>
      </div>

      {errorMessage ? <p className="text-sm text-red-600">{errorMessage}</p> : null}

      <div className="flex items-center justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="rounded-md border border-neutral-200 bg-white px-4 py-2 text-sm font-medium hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? 'Saving...' : submitLabel}
        </button>
      </div>
    </form>
  )
}

