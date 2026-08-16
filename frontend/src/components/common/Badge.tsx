import React from 'react';
import styles from '../../styles/components.module.css';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral';
  className?: string;
}

const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral', className }) => {
  const baseClass = styles.badge;
  const variantClass = styles[`badge-${variant}`];
  const combinedClass = `${baseClass} ${variantClass} ${className || ''}`.trim();

  return (
    <span className={combinedClass}>
      {children}
    </span>
  );
};

export default Badge;
