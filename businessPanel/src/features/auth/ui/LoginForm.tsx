import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

export const loginFormSchema = z.object({
  email: z.string().trim().min(1, 'Email is required'),
  password: z.string().min(1, 'Password is required'),
})

export type LoginFormValues = z.infer<typeof loginFormSchema>

type LoginFormProps = {
  onSubmit: (values: LoginFormValues) => Promise<void> | void
  isSubmitting?: boolean
  errorMessage?: string | null
}

export function LoginForm({ onSubmit, isSubmitting, errorMessage }: LoginFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: { email: '', password: '' },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-1">
        <label htmlFor="email" className="text-sm font-medium text-neutral-900">
          Email
        </label>
        <input
          id="email"
          type="text"
          autoComplete="username"
          disabled={isSubmitting}
          {...register('email')}
          className="w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400 disabled:cursor-not-allowed disabled:opacity-60"
        />
        {errors.email?.message ? (
          <p className="text-xs text-red-600">{errors.email.message}</p>
        ) : null}
      </div>

      <div className="space-y-1">
        <label htmlFor="password" className="text-sm font-medium text-neutral-900">
          Password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          disabled={isSubmitting}
          {...register('password')}
          className="w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm outline-none focus:border-neutral-400 disabled:cursor-not-allowed disabled:opacity-60"
        />
        {errors.password?.message ? (
          <p className="text-xs text-red-600">{errors.password.message}</p>
        ) : null}
      </div>

      {errorMessage ? <p className="text-sm text-red-600">{errorMessage}</p> : null}

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isSubmitting ? 'Signing in...' : 'Sign in'}
      </button>
    </form>
  )
}

