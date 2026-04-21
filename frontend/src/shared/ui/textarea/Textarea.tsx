import { type TextareaHTMLAttributes, forwardRef } from 'react';
import cn from 'classnames';
import styles from '../input/Input.module.scss';

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, className, id, ...rest }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-');
    return (
      <div className={styles.wrapper}>
        {label && <label htmlFor={inputId} className={styles.label}>{label}</label>}
        <textarea
          id={inputId}
          ref={ref}
          className={cn(styles.input, { [styles['input--error']]: !!error }, className)}
          {...rest}
        />
        {error && <p className={styles.error}>{error}</p>}
      </div>
    );
  },
);

Textarea.displayName = 'Textarea';
