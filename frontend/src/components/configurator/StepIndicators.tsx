import React, { useState } from 'react';
import { useJobStore } from '../../store/jobStore';
import styles from '../../styles/pages.module.css';

const INDICATORS = {
  momentum: ['RSI', 'MACD', 'Stochastic', 'Williams %R', 'CCI', 'ROC', 'Awesome Oscillator'],
  trend: ['ADX', 'Aroon', 'PSAR', 'TRIX'],
  volatility: ['Bollinger Bands', 'ATR', 'Keltner Channel', 'Donchian Channel'],
  volume: ['OBV', 'MFI', 'VWAP'],
  overlap: ['EMA', 'SMA', 'HMA', 'WMA']
};

const StepIndicators: React.FC = () => {
  const { config, toggleIndicator } = useJobStore();
  const [activeTab, setActiveTab] = useState<keyof typeof INDICATORS>('momentum');

  const categories = Object.keys(INDICATORS) as Array<keyof typeof INDICATORS>;

  return (
    <div className={styles.stepContainer}>
      <h2 className={styles.stepTitle}>Indicators</h2>
      <p className={styles.stepSubtitle}>Select indicators for the genetic algorithm to use as building blocks.</p>

      <div className={styles.indicatorTabs}>
        {categories.map(cat => (
          <button 
            key={cat}
            className={`${styles.indicatorTab} ${activeTab === cat ? styles.indicatorTabActive : ''}`}
            onClick={() => setActiveTab(cat)}
          >
            {cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}
      </div>

      <div className={styles.indicatorGrid}>
        {INDICATORS[activeTab].map(ind => {
          const isSelected = config.indicators.includes(ind);
          return (
            <div 
              key={ind} 
              className={`${styles.indicatorCard} ${isSelected ? styles.indicatorCardSelected : ''}`}
              onClick={() => toggleIndicator(ind, !isSelected)}
            >
              <div className={styles.indicatorHeader}>
                <span className={styles.indicatorName}>{ind}</span>
                <input 
                  type="checkbox" 
                  checked={isSelected}
                  onChange={() => {}}
                  className={styles.checkbox}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default StepIndicators;
