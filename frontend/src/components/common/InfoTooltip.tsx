import React, { useState } from 'react';
import { Info } from 'lucide-react';
import styles from '../../styles/components.module.css';

interface InfoTooltipProps {
  content: string | React.ReactNode;
  title?: string;
}

export const InfoTooltip: React.FC<InfoTooltipProps> = ({ content, title }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={styles.tooltipContainer} onMouseEnter={() => setIsOpen(true)} onMouseLeave={() => setIsOpen(false)}>
      <button 
        type="button" 
        className={styles.infoBadge}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
        aria-label="More information"
      >
        <Info size={12} strokeWidth={2.5} />
      </button>

      {isOpen && (
        <div className={styles.tooltipPopover} onClick={(e) => e.stopPropagation()}>
          {title && <div className={styles.tooltipTitle}>{title}</div>}
          <div className={styles.tooltipContent}>{content}</div>
        </div>
      )}
    </div>
  );
};

export default InfoTooltip;
