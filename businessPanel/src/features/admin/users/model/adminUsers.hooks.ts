import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '../../../../shared/api'
import { adminUsersApi } from '../api/adminUsers.api'
import type { UpdateUserRolePayload } from './adminUsers.types'

export function useAdminUsersQuery() {
  return useQuery({
    queryKey: queryKeys.admin.users.list,
    queryFn: () => adminUsersApi.getAdminUsers(),
  })
}

export function useAdminUserDetailsQuery(userId: number, enabled = true) {
  return useQuery({
    queryKey: queryKeys.admin.users.details(userId),
    queryFn: () => adminUsersApi.getAdminUserDetails(userId),
    enabled: enabled && Number.isFinite(userId),
  })
}

export function useUpdateAdminUserRoleMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ userId, payload }: { userId: number; payload: UpdateUserRolePayload }) =>
      adminUsersApi.updateAdminUserRole(userId, payload),
    onSuccess: async (_data, variables) => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.admin.users.root })
      await queryClient.invalidateQueries({
        queryKey: queryKeys.admin.users.details(variables.userId),
      })
    },
  })
}

