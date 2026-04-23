import { z } from 'zod'

export const updateUserRoleSchema = z.object({
  role: z.enum(['user', 'business', 'admin']),
})

export type UpdateUserRoleFormValues = z.infer<typeof updateUserRoleSchema>

