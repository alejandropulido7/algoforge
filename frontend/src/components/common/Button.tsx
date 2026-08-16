import React from 'react';
import styles from '../../styles/components.module.css';
import Spinner from './Spinner';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  isLoading = false, 
  disabled, 
  className,
  ...props 
}) => {
  const baseClass = styles.btn;
  const variantClass = styles[`btn-${variant}`];
  const sizeClass = styles[`btn-${size}`];
  const combinedClass = `${baseClass} ${variantClass} ${sizeClass} ${className || ''}`.trim();

  return (
    <button 
      className={combinedClass} 
      disabled={isLoading || disabled} 
      {...props}
    >
      {isLoading ? <Spinner size="sm" /> : children}
    </button>
  );
};

export default Button;
