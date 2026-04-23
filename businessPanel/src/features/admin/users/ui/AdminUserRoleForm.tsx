import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'

import type { AdminUserDetails, UserRole } from '../model/adminUsers.types'
import { updateUserRoleSchema, type UpdateUserRoleFormValues } from '../model/adminUsers.schemas'
import { useUpdateAdminUserRoleMutation } from '../model/adminUsers.hooks'
import { getErrorMessage } from '../../../../shared/lib/getErrorMessage'
import { SectionCard } from '../../../../shared/ui/SectionCard'

const roleOptions: { value: UserRole; label: string }[] = [
  { value: 'user', label: 'User' },
  { value: 'business', label: 'Business' },
  { value: 'admin', label: 'Admin' },
]

type AdminUserRoleFormProps = {
  user: AdminUserDetails
  currentAdminId: number | null
}

export function AdminUserRoleForm({ user, currentAdminId }: AdminUserRoleFormProps) {
  const mutation = useUpdateAdminUserRoleMutation()

  const isSelf = currentAdminId != null && currentAdminId === user.id

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<UpdateUserRoleFormValues>({
    resolver: zodResolver(updateUserRoleSchema),
    defaultValues: { role: user.role },
  })

  useEffect(() => {
    reset({ role: user.role })
  }, [reset, user.role])

  return (
    <SectionCard
      title="Update role"
      description="Role changes affect dashboard access and moderation permissions."
    >
      {isSelf ? (
        <p className="text-sm text-neutral-700">
          You cannot change your own role.
        </p>
      ) : (
        <form
          onSubmit={handleSubmit(async (values) => {
            await mutation.mutateAsync({ userId: user.id, payload: values })
          })}
          className="space-y-4"
        >
          <div className="space-y-1">
            <label htmlFor="role" className="text-sm font-medium text-neutral-900">
              Role
            </label>
            <select
              id="role"
              disabled={mutation.isPending}
              {...register('role')}
              className="w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {roleOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            {errors.role?.message ? (
              <p className="text-xs text-red-600">{errors.role.message}</p>
            ) : null}
          </div>

          {mutation.isError ? (
            <p className="text-sm text-red-600">
              {getErrorMessage(mutation.error, 'Failed to update role')}
            </p>
          ) : null}

          <button
            type="submit"
            disabled={mutation.isPending || !isDirty}
            className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {mutation.isPending ? 'Updating...' : 'Update role'}
          </button>
        </form>
      )}
    </SectionCard>
  )
}

