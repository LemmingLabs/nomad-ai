import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router-dom';
import { loginSchema, type LoginFormData } from '../../features/auth/login-by-email';
import { registerSchema, type RegisterFormData } from '../../features/auth/register-by-email';
import { Button } from '../../shared/ui/button/Button';
import { Input } from '../../shared/ui/input/Input';
import { Divider } from '../../shared/ui/divider/Divider';
import styles from './AuthForm.module.scss';

// ─── Login Form ───────────────────────────────────────────────────────────────
interface LoginFormProps {
  onSubmit: (data: LoginFormData) => void;
  isLoading?: boolean;
}

export function LoginForm({ onSubmit, isLoading }: LoginFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  return (
    <form
      className={styles.form}
      onSubmit={(event) => {
        void handleSubmit(onSubmit)(event);
      }}
    >
      <div className={styles.header}>
        <h1 className={styles.title}>Welcome back</h1>
        <p className={styles.subtitle}>Sign in to your NomadAI account</p>
      </div>

      <div className={styles.fields}>
        <Input label="Email" type="email" placeholder="you@example.com" error={errors.email?.message} {...register('email')} />
        <Input label="Password" type="password" placeholder="••••••••" error={errors.password?.message} {...register('password')} />
      </div>

      <Button type="submit" fullWidth size="lg" isLoading={isLoading}>Sign In</Button>

      <Divider label="or" />

      <p className={styles.switch}>
        Don't have an account? <Link to="/auth/register" className={styles.link}>Create one</Link>
      </p>
    </form>
  );
}

// ─── Register Form ────────────────────────────────────────────────────────────
interface RegisterFormProps {
  onSubmit: (data: RegisterFormData) => void;
  isLoading?: boolean;
}

export function RegisterForm({ onSubmit, isLoading }: RegisterFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  return (
    <form
      className={styles.form}
      onSubmit={(event) => {
        void handleSubmit(onSubmit)(event);
      }}
    >
      <div className={styles.header}>
        <h1 className={styles.title}>Create account</h1>
        <p className={styles.subtitle}>Start planning your dream trips with AI</p>
      </div>

      <div className={styles.fields}>
        <Input label="Email" type="email" placeholder="you@example.com" error={errors.email?.message} {...register('email')} />
        <Input label="Password" type="password" placeholder="••••••••" error={errors.password?.message} {...register('password')} />
        <Input label="Confirm password" type="password" placeholder="••••••••" error={errors.confirm_password?.message} {...register('confirm_password')} />
      </div>

      <Button type="submit" fullWidth size="lg" isLoading={isLoading}>Create Account</Button>

      <Divider label="or" />

      <p className={styles.switch}>
        Already have an account? <Link to="/auth/login" className={styles.link}>Sign in</Link>
      </p>
    </form>
  );
}
