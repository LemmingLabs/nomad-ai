import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'

import { businessMediaFormSchema } from '../model/businessMedia.schemas'
import type { BusinessMediaFormValues } from '../model/businessMedia.types'

type BusinessMediaFormProps = {
  isSubmitting: boolean
  onSubmit: (values: BusinessMediaFormValues) => void | Promise<void>
}

export function BusinessMediaForm({ isSubmitting, onSubmit }: BusinessMediaFormProps) {
  const form = useForm<BusinessMediaFormValues>({
    resolver: zodResolver(businessMediaFormSchema),
    defaultValues: { type: 'image', url: '' },
    mode: 'onSubmit',
  })

  const handleSubmit = async (values: BusinessMediaFormValues) => {
    await onSubmit({ ...values, url: values.url.trim() })
    form.reset({ type: values.type, url: '' })
  }

  return (
    <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div>
          <label className="block text-sm font-medium text-neutral-700">Type</label>
          <select
            className="mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
            {...form.register('type')}
            disabled={isSubmitting}
          >
            <option value="image">Image</option>
            <option value="logo">Logo</option>
          </select>
          {form.formState.errors.type?.message ? (
            <p className="mt-1 text-sm text-red-600">
              {form.formState.errors.type.message}
            </p>
          ) : null}
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-neutral-700">URL</label>
          <input
            className="mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
            placeholder="https://example.com/image.png"
            {...form.register('url')}
            disabled={isSubmitting}
          />
          {form.formState.errors.url?.message ? (
            <p className="mt-1 text-sm text-red-600">
              {form.formState.errors.url.message}
            </p>
          ) : null}
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="inline-flex items-center justify-center rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isSubmitting ? 'Adding...' : 'Add media'}
      </button>
    </form>
  )
}

