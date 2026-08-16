import React, { forwardRef } from 'react';
import InfoTooltip from './InfoTooltip';
import styles from '../../styles/components.module.css';

interface SelectOption {
  label: string;
  value: string | number;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
  error?: string;
  tooltip?: string | React.ReactNode;
  tooltipTitle?: string;
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(({ 
  label, 
  options, 
  error, 
  tooltip, 
  tooltipTitle,
  className, 
  ...props 
}, ref) => {
  const selectId = props.id || props.name || Math.random().toString(36).substring(7);

  return (
    <div className={styles.inputGroup}>
      {label && (
        <div className={styles.labelWrapper}>
          <label htmlFor={selectId} className={styles.label}>{label}</label>
          {tooltip && <InfoTooltip content={tooltip} title={tooltipTitle || label} />}
        </div>
      )}
      <div className={styles.selectWrapper}>
        <select
          ref={ref}
          id={selectId}
          className={`${styles.select} ${error ? styles.inputError : ''} ${className || ''}`}
          {...props}
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <div className={styles.selectArrow}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </div>
      </div>
      {error && <span className={styles.errorText}>{error}</span>}
    </div>
  );
});

Select.displayName = 'Select';
export default Select;
