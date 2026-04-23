import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'

import { businessProfileFormSchema } from '../model/businessProfile.schemas'
import type { BusinessProfileFormValues } from '../model/businessProfile.types'

type BusinessProfileFormProps = {
  initialValues: BusinessProfileFormValues
  submitLabel: string
  isSubmitting: boolean
  onSubmit: (values: BusinessProfileFormValues) => void | Promise<void>
}

export function BusinessProfileForm({
  initialValues,
  submitLabel,
  isSubmitting,
  onSubmit,
}: BusinessProfileFormProps) {
  const form = useForm<BusinessProfileFormValues>({
    resolver: zodResolver(businessProfileFormSchema),
    defaultValues: initialValues,
    mode: 'onSubmit',
  })

  useEffect(() => {
    form.reset(initialValues)
  }, [form, initialValues])

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-neutral-700">Name</label>
        <input
          className="mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
          placeholder="Business name"
          {...form.register('name')}
          disabled={isSubmitting}
        />
        {form.formState.errors.name?.message ? (
          <p className="mt-1 text-sm text-red-600">
            {form.formState.errors.name.message}
          </p>
        ) : null}
      </div>

      <div>
        <label className="block text-sm font-medium text-neutral-700">
          Description
        </label>
        <textarea
          className="mt-1 min-h-28 w-full resize-y rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
          placeholder="Describe your business"
          {...form.register('description')}
          disabled={isSubmitting}
        />
        {form.formState.errors.description?.message ? (
          <p className="mt-1 text-sm text-red-600">
            {form.formState.errors.description.message}
          </p>
        ) : null}
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-neutral-700">
            Contact phone
          </label>
          <input
            className="mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
            placeholder="+1 555 555 5555"
            {...form.register('contact_phone')}
            disabled={isSubmitting}
          />
          {form.formState.errors.contact_phone?.message ? (
            <p className="mt-1 text-sm text-red-600">
              {form.formState.errors.contact_phone.message}
            </p>
          ) : null}
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700">
            Website URL
          </label>
          <input
            className="mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
            placeholder="https://example.com"
            {...form.register('website_url')}
            disabled={isSubmitting}
          />
          {form.formState.errors.website_url?.message ? (
            <p className="mt-1 text-sm text-red-600">
              {form.formState.errors.website_url.message}
            </p>
          ) : null}
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="inline-flex items-center justify-center rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isSubmitting ? 'Saving...' : submitLabel}
      </button>
    </form>
  )
}

