import React, { forwardRef } from 'react';
import InfoTooltip from './InfoTooltip';
import styles from '../../styles/components.module.css';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
  tooltip?: string | React.ReactNode;
  tooltipTitle?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(({ 
  label, 
  error, 
  helperText, 
  icon, 
  tooltip, 
  tooltipTitle,
  className, 
  ...props 
}, ref) => {
  const inputId = props.id || props.name || Math.random().toString(36).substring(7);

  return (
    <div className={styles.inputGroup}>
      {label && (
        <div className={styles.labelWrapper}>
          <label htmlFor={inputId} className={styles.label}>{label}</label>
          {tooltip && <InfoTooltip content={tooltip} title={tooltipTitle || label} />}
        </div>
      )}
      <div className={styles.inputWrapper}>
        {icon && <div className={styles.inputIcon}>{icon}</div>}
        <input
          ref={ref}
          id={inputId}
          className={`${styles.input} ${error ? styles.inputError : ''} ${icon ? styles.inputWithIcon : ''} ${className || ''}`}
          {...props}
        />
      </div>
      {error && <span className={styles.errorText}>{error}</span>}
      {!error && helperText && <span className={styles.helperText}>{helperText}</span>}
    </div>
  );
});

Input.displayName = 'Input';
export default Input;
