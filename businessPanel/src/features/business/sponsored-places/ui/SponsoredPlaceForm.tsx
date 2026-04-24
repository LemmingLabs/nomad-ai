import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect, useState } from 'react'
import { Controller, useForm } from 'react-hook-form'

import { env } from '../../../../shared/config/env'
import { sponsoredPlaceFormSchema } from '../model/sponsoredPlaces.schemas'
import type {
  SponsoredPlaceFormValues,
  SponsoredPlaceLocationValue,
} from '../model/sponsoredPlaces.types'
import { formatKyrgyzPhoneInput } from '../model/sponsoredPlaces.utils'
import { SponsoredPlaceLocationPicker } from './SponsoredPlaceLocationPicker'

type SponsoredPlaceFormProps = {
  initialValues: SponsoredPlaceFormValues
  submitLabel: string
  isSubmitting: boolean
  onCancel?: () => void
  onSubmit: (values: SponsoredPlaceFormValues) => void | Promise<void>
}

export function SponsoredPlaceForm({
  initialValues,
  submitLabel,
  isSubmitting,
  onCancel,
  onSubmit,
}: SponsoredPlaceFormProps) {
  const [cityWasEditedManually, setCityWasEditedManually] = useState(
    initialValues.city.trim() !== '',
  )

  const form = useForm<SponsoredPlaceFormValues>({
    resolver: zodResolver(sponsoredPlaceFormSchema),
    defaultValues: initialValues,
    mode: 'onSubmit',
  })

  useEffect(() => {
    setCityWasEditedManually(initialValues.city.trim() !== '')
    form.reset({
      ...initialValues,
      contact_phone: formatKyrgyzPhoneInput(initialValues.contact_phone),
    })
  }, [form, initialValues])

  const watchedLocation: SponsoredPlaceLocationValue = {
    lat: form.watch('lat'),
    lng: form.watch('lng'),
    address: form.watch('address'),
    city: form.watch('city'),
  }

  const googleMapsConfigured = env.googleMapsApiKey !== ''
  const locationError =
    form.formState.errors.lat?.message ?? form.formState.errors.lng?.message

  const handleLocationChange = (location: SponsoredPlaceLocationValue) => {
    form.setValue('lat', location.lat, { shouldDirty: true, shouldValidate: true })
    form.setValue('lng', location.lng, { shouldDirty: true, shouldValidate: true })
    form.setValue('address', location.address, {
      shouldDirty: true,
      shouldValidate: true,
    })
    form.setValue('city', location.city, { shouldDirty: true, shouldValidate: true })
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <SponsoredPlaceLocationPicker
        value={watchedLocation}
        disabled={isSubmitting}
        shouldAutofillCity={!cityWasEditedManually}
        onChange={handleLocationChange}
      />
      {locationError ? (
        <p className="text-sm text-red-600">{locationError as string}</p>
      ) : null}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="block text-sm font-medium text-neutral-700">Title</label>
          <input
            className="mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
            {...form.register('title')}
            disabled={isSubmitting}
          />
          {form.formState.errors.title?.message ? (
            <p className="mt-1 text-sm text-red-600">
              {form.formState.errors.title.message}
            </p>
          ) : null}
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700">City</label>
          <Controller
            control={form.control}
            name="city"
            render={({ field }) => (
              <input
                value={field.value}
                onChange={(event) => {
                  setCityWasEditedManually(true)
                  field.onChange(event.target.value)
                }}
                onBlur={field.onBlur}
                name={field.name}
                ref={field.ref}
                className="mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
                disabled={isSubmitting}
              />
            )}
          />
          {form.formState.errors.city?.message ? (
            <p className="mt-1 text-sm text-red-600">
              {form.formState.errors.city.message}
            </p>
          ) : null}
          <p className="mt-1 text-xs text-neutral-500">
            Confirm the city manually if Google Places suggests the wrong region.
          </p>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-neutral-700">
          Description
        </label>
        <textarea
          className="mt-1 min-h-28 w-full resize-y rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
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
            Category
          </label>
          <input
            className="mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
            {...form.register('category')}
            disabled={isSubmitting}
          />
          {form.formState.errors.category?.message ? (
            <p className="mt-1 text-sm text-red-600">
              {form.formState.errors.category.message}
            </p>
          ) : null}
        </div>

        <div>
          <label className="block text-sm font-medium text-neutral-700">
            Address
          </label>
          <input
            className="mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
            {...form.register('address')}
            disabled={isSubmitting}
          />
          {form.formState.errors.address?.message ? (
            <p className="mt-1 text-sm text-red-600">
              {form.formState.errors.address.message}
            </p>
          ) : null}
        </div>
      </div>

      {googleMapsConfigured ? (
        <>
          <input type="hidden" {...form.register('lat')} />
          <input type="hidden" {...form.register('lng')} />
        </>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-neutral-700">Lat</label>
            <input
              type="number"
              step="any"
              className="mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
              {...form.register('lat')}
              disabled={isSubmitting}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700">Lng</label>
            <input
              type="number"
              step="any"
              className="mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
              {...form.register('lng')}
              disabled={isSubmitting}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div>
          <label className="block text-sm font-medium text-neutral-700">
            Contact phone
          </label>
          <Controller
            control={form.control}
            name="contact_phone"
            render={({ field }) => (
              <input
                value={field.value}
                onChange={(event) =>
                  field.onChange(formatKyrgyzPhoneInput(event.target.value))
                }
                onBlur={field.onBlur}
                name={field.name}
                ref={field.ref}
                placeholder="+996 700 123 456"
                className="mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
                disabled={isSubmitting}
                inputMode="numeric"
              />
            )}
          />
          {form.formState.errors.contact_phone?.message ? (
            <p className="mt-1 text-sm text-red-600">
              {form.formState.errors.contact_phone.message}
            </p>
          ) : null}
        </div>

        <div className="md:col-span-2">
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

      <div>
        <label className="block text-sm font-medium text-neutral-700">CTA text</label>
        <input
          className="mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400"
          {...form.register('cta_text')}
          disabled={isSubmitting}
        />
        {form.formState.errors.cta_text?.message ? (
          <p className="mt-1 text-sm text-red-600">
            {form.formState.errors.cta_text.message}
          </p>
        ) : null}
      </div>

      <div className="flex items-center gap-2">
        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex items-center justify-center rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isSubmitting ? 'Saving...' : submitLabel}
        </button>

        {onCancel ? (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="rounded-md border border-neutral-200 bg-white px-4 py-2 text-sm font-medium hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Cancel
          </button>
        ) : null}
      </div>
    </form>
  )
}
