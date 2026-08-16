import React from 'react';
import styles from '../../styles/components.module.css';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

const Spinner: React.FC<SpinnerProps> = ({ size = 'md', color = 'var(--color-accent-cyan)' }) => {
  const sizeMap = {
    sm: '16px',
    md: '24px',
    lg: '36px'
  };

  return (
    <div 
      className={styles.spinner} 
      style={{ 
        width: sizeMap[size], 
        height: sizeMap[size],
        borderTopColor: color,
        borderRightColor: color
      }} 
    />
  );
};

export default Spinner;
