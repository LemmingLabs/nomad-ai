import { type InputHTMLAttributes, type ReactNode, forwardRef } from 'react';
import cn from 'classnames';
import styles from './Input.module.scss';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  iconLeft?: ReactNode;
  iconRight?: ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, iconLeft, iconRight, className, id, ...rest }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-');
    return (
      <div className={styles.wrapper}>
        {label && <label htmlFor={inputId} className={styles.label}>{label}</label>}
        <div className={styles.inputWrap}>
          {iconLeft && <span className={styles.iconLeft}>{iconLeft}</span>}
          <input
            id={inputId}
            ref={ref}
            className={cn(
              styles.input,
              { [styles['input--error']]: !!error,
                [styles['input--with-icon-left']]: !!iconLeft,
                [styles['input--with-icon-right']]: !!iconRight },
              className,
            )}
            {...rest}
          />
          {iconRight && <span className={styles.iconRight}>{iconRight}</span>}
        </div>
        {error && <p className={styles.error}>{error}</p>}
      </div>
    );
  },
);

Input.displayName = 'Input';
