import React, { useState, useMemo } from 'react';
import { useJobStore } from '../../store/jobStore';
import { Search, CheckSquare, Square, Info } from 'lucide-react';
import styles from '../../styles/pages.module.css';

interface IndicatorItem {
  id: string;
  name: string;
  category: 'momentum' | 'trend' | 'volatility' | 'volume' | 'others';
  desc: string;
  detail: string;
}

const ALL_INDICATORS: IndicatorItem[] = [
  // === Momentum (11) ===
  { id: 'RSI', name: 'RSI', category: 'momentum', desc: 'Relative Strength Index', detail: 'Measures momentum of recent price changes to evaluate overbought and oversold conditions.' },
  { id: 'Stochastic', name: 'Stochastic Oscillator', category: 'momentum', desc: 'Stochastic %K & %D', detail: 'Compares a specific closing price to a range of its prices over a set period.' },
  { id: 'StochRSI', name: 'StochRSI', category: 'momentum', desc: 'Stochastic RSI', detail: 'Applies Stochastic formula to RSI values, providing high sensitivity to momentum shifts.' },
  { id: 'TSI', name: 'TSI', category: 'momentum', desc: 'True Strength Index', detail: 'Variation of RSI using double smoothed price momentum to filter whipsaws.' },
  { id: 'Ultimate Oscillator', name: 'Ultimate Oscillator', category: 'momentum', desc: 'Triple Timeframe Momentum', detail: 'Combines short, intermediate, and long timeframes (7, 14, 28) to avoid false divergence.' },
  { id: 'Williams %R', name: 'Williams %R', category: 'momentum', desc: 'Williams Percent Range', detail: 'Momentum indicator reflecting the level of the close relative to the high-low range.' },
  { id: 'Awesome Oscillator', name: 'Awesome Oscillator', category: 'momentum', desc: 'Bill Williams AO', detail: 'Market momentum calculated from the difference of a 34-period and 5-period SMA.' },
  { id: 'KAMA', name: 'KAMA', category: 'momentum', desc: "Kaufman's Adaptive MA", detail: 'Moving average that accounts for market noise and trend speed.' },
  { id: 'ROC', name: 'ROC', category: 'momentum', desc: 'Rate of Change', detail: 'Pure momentum oscillator that measures percentage change between current and past price.' },
  { id: 'PPO', name: 'PPO', category: 'momentum', desc: 'Percentage Price Oscillator', detail: 'Percentage version of MACD allowing comparison across assets with different prices.' },
  { id: 'PVO', name: 'PVO', category: 'momentum', desc: 'Percentage Volume Oscillator', detail: 'Measures volume momentum as percentage difference between fast and slow volume EMAs.' },

  // === Trend (16) ===
  { id: 'MACD', name: 'MACD', category: 'trend', desc: 'Moving Avg Convergence Divergence', detail: 'Trend-following momentum indicator showing relationship between two price moving averages.' },
  { id: 'SMA', name: 'SMA', category: 'trend', desc: 'Simple Moving Average', detail: 'Arithmetic mean of closing prices over selected lookback window.' },
  { id: 'EMA', name: 'EMA', category: 'trend', desc: 'Exponential Moving Average', detail: 'Weighted moving average giving greater weight to recent price data.' },
  { id: 'WMA', name: 'WMA', category: 'trend', desc: 'Weighted Moving Average', detail: 'Linearly weighted average prioritizing recent bars.' },
  { id: 'HMA', name: 'HMA', category: 'trend', desc: 'Hull Moving Average', detail: 'Extremely responsive moving average with virtually eliminated lag.' },
  { id: 'ADX', name: 'ADX', category: 'trend', desc: 'Average Directional Index', detail: 'Quantifies trend strength regardless of whether price is moving up or down.' },
  { id: 'Aroon', name: 'Aroon Oscillator', category: 'trend', desc: 'Aroon Up / Down', detail: 'Tracks time taken between highs and lows to anticipate trend breakouts.' },
  { id: 'CCI', name: 'CCI', category: 'trend', desc: 'Commodity Channel Index', detail: 'Identifies cyclical trends by measuring price relative to its statistical average.' },
  { id: 'PSAR', name: 'PSAR', category: 'trend', desc: 'Parabolic Stop and Reverse', detail: 'Trailing price envelope used for trend detection and stop loss placement.' },
  { id: 'Ichimoku', name: 'Ichimoku Kinko Hyo', category: 'trend', desc: 'Kijun-sen Base Line', detail: 'Comprehensive Japanese indicator providing support, resistance, and trend direction.' },
  { id: 'KST', name: 'KST', category: 'trend', desc: 'Know Sure Thing Oscillator', detail: 'Martin Pring momentum oscillator combining four smoothed rate-of-change cycles.' },
  { id: 'DPO', name: 'DPO', category: 'trend', desc: 'Detrended Price Oscillator', detail: 'Removes long-term trend from price to isolate short-term cycles.' },
  { id: 'TRIX', name: 'TRIX', category: 'trend', desc: 'Triple Smoothed EMA', detail: 'Oscillator filtering out minor cycles to identify major turning points.' },
  { id: 'Mass Index', name: 'Mass Index', category: 'trend', desc: 'Mass Index Reversal', detail: 'Detects range expansions to anticipate trend reversals.' },
  { id: 'Vortex', name: 'Vortex Indicator', category: 'trend', desc: 'Vortex VI+', detail: 'Two oscillating lines identifying start of a new positive or negative trend.' },
  { id: 'STC', name: 'STC', category: 'trend', desc: 'Schaff Trend Cycle', detail: 'Cyclical momentum oscillator combining MACD and Stochastics.' },

  // === Volatility (5) ===
  { id: 'ATR', name: 'ATR', category: 'volatility', desc: 'Average True Range', detail: 'Standard measure of market volatility across high, low, and prior close.' },
  { id: 'Bollinger Bands', name: 'Bollinger Bands', category: 'volatility', desc: '%B / Bandwidth', detail: 'Standard deviation envelope around a moving average measuring relative volatility.' },
  { id: 'Keltner Channel', name: 'Keltner Channel', category: 'volatility', desc: 'ATR Volatility Envelope', detail: 'Moving average envelope with distance set by Average True Range.' },
  { id: 'Donchian Channel', name: 'Donchian Channel', category: 'volatility', desc: 'Price High/Low Channel', detail: 'Channel formed by highest high and lowest low over lookback period.' },
  { id: 'Ulcer Index', name: 'Ulcer Index', category: 'volatility', desc: 'Drawdown Risk Metric', detail: 'Measures downside risk by assessing the depth and duration of price drawdowns.' },

  // === Volume (9) ===
  { id: 'OBV', name: 'OBV', category: 'volume', desc: 'On-Balance Volume', detail: 'Cumulative volume flow indicator associating volume with price movements.' },
  { id: 'VWAP', name: 'VWAP', category: 'volume', desc: 'Volume-Weighted Average Price', detail: 'Average price weighted by volume giving the true institutional benchmark.' },
  { id: 'MFI', name: 'MFI', category: 'volume', desc: 'Money Flow Index', detail: 'Volume-weighted RSI measuring buying and selling pressure.' },
  { id: 'ADI', name: 'ADI', category: 'volume', desc: 'Accumulation/Distribution', detail: 'Gauges cumulative flow of money in and out of a security.' },
  { id: 'CMF', name: 'CMF', category: 'volume', desc: 'Chaikin Money Flow', detail: 'Measures amount of money flow volume over a specified period.' },
  { id: 'Force Index', name: 'Force Index', category: 'volume', desc: 'Alexander Elder Force Index', detail: 'Combines price change and volume to measure the power behind price moves.' },
  { id: 'Ease of Movement', name: 'Ease of Movement', category: 'volume', desc: 'EoM Oscillator', detail: 'Relates price changes to volume to determine ease of price traversal.' },
  { id: 'NVI', name: 'NVI', category: 'volume', desc: 'Negative Volume Index', detail: 'Identifies institutional smart money activity on lower volume bars.' },
  { id: 'VPT', name: 'VPT', category: 'volume', desc: 'Volume-Price Trend', detail: 'Combines percentage price changes and volume to confirm trend health.' },

  // === Returns & Others (3) ===
  { id: 'Daily Return', name: 'Daily Return', category: 'others', desc: 'Percentage Return', detail: 'Percentage price change per bar.' },
  { id: 'Daily Log Return', name: 'Daily Log Return', category: 'others', desc: 'Logarithmic Return', detail: 'Logarithmic return useful for compounding asset analysis.' },
  { id: 'Cumulative Return', name: 'Cumulative Return', category: 'others', desc: 'Total Cumulative Return', detail: 'Cumulative price return from the start of the series.' },
];

const StepIndicators: React.FC = () => {
  const { config, toggleIndicator } = useJobStore();
  const [activeCategory, setActiveCategory] = useState<'all' | 'momentum' | 'trend' | 'volatility' | 'volume' | 'others'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const categories = [
    { id: 'all', label: 'All Indicators', count: ALL_INDICATORS.length },
    { id: 'momentum', label: 'Momentum', count: ALL_INDICATORS.filter(i => i.category === 'momentum').length },
    { id: 'trend', label: 'Trend & Overlap', count: ALL_INDICATORS.filter(i => i.category === 'trend').length },
    { id: 'volatility', label: 'Volatility', count: ALL_INDICATORS.filter(i => i.category === 'volatility').length },
    { id: 'volume', label: 'Volume', count: ALL_INDICATORS.filter(i => i.category === 'volume').length },
    { id: 'others', label: 'Returns & Stats', count: ALL_INDICATORS.filter(i => i.category === 'others').length },
  ];

  const filteredIndicators = useMemo(() => {
    return ALL_INDICATORS.filter(item => {
      const matchCat = activeCategory === 'all' || item.category === activeCategory;
      const matchSearch = searchQuery === '' || 
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
        item.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.desc.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [activeCategory, searchQuery]);

  const handleSelectAllInView = () => {
    filteredIndicators.forEach(ind => {
      if (!config.indicators.includes(ind.id)) {
        toggleIndicator(ind.id, true);
      }
    });
  };

  const handleDeselectAllInView = () => {
    filteredIndicators.forEach(ind => {
      if (config.indicators.includes(ind.id)) {
        toggleIndicator(ind.id, false);
      }
    });
  };

  return (
    <div className={styles.stepContainer}>
      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className={styles.stepTitle}>Technical Indicators (TA Library)</h2>
          <p className={styles.stepSubtitle}>
            Select indicators for the genetic algorithm to use as evolutionary building blocks ({config.indicators.length} selected).
          </p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
        <div style={{ position: 'relative', minWidth: '260px', flex: 1, maxWidth: '400px' }}>
          <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
          <input
            type="text"
            placeholder="Search 40+ indicators (e.g. RSI, KST, VWAP)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem 0.75rem 0.5rem 2.25rem',
              borderRadius: '6px',
              border: '1px solid var(--color-border)',
              background: 'var(--color-bg-card)',
              color: 'var(--color-text-main)',
              fontSize: '0.875rem',
              outline: 'none'
            }}
          />
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            type="button"
            onClick={handleSelectAllInView}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              padding: '0.4rem 0.75rem',
              borderRadius: '6px',
              fontSize: '0.8125rem',
              background: 'rgba(0, 212, 255, 0.1)',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              color: 'var(--color-accent-cyan)',
              cursor: 'pointer'
            }}
          >
            <CheckSquare size={14} />
            <span>Select Visible ({filteredIndicators.length})</span>
          </button>
          <button
            type="button"
            onClick={handleDeselectAllInView}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.375rem',
              padding: '0.4rem 0.75rem',
              borderRadius: '6px',
              fontSize: '0.8125rem',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-muted)',
              cursor: 'pointer'
            }}
          >
            <Square size={14} />
            <span>Clear Visible</span>
          </button>
        </div>
      </div>

      {/* Category Tabs */}
      <div className={styles.indicatorTabs} style={{ marginBottom: '1.25rem' }}>
        {categories.map(cat => (
          <button 
            key={cat.id}
            className={`${styles.indicatorTab} ${activeCategory === cat.id ? styles.indicatorTabActive : ''}`}
            onClick={() => setActiveCategory(cat.id as any)}
            style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}
          >
            <span>{cat.label}</span>
            <span style={{ fontSize: '0.6875rem', opacity: 0.7, background: 'rgba(255,255,255,0.1)', padding: '0.1rem 0.35rem', borderRadius: '10px' }}>
              {cat.count}
            </span>
          </button>
        ))}
      </div>

      {/* Indicators Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '0.875rem' }}>
        {filteredIndicators.map(ind => {
          const isSelected = config.indicators.includes(ind.id);
          return (
            <div 
              key={ind.id} 
              onClick={() => toggleIndicator(ind.id, !isSelected)}
              style={{
                background: isSelected ? 'rgba(0, 212, 255, 0.08)' : 'var(--color-bg-card)',
                border: isSelected ? '1px solid var(--color-accent-cyan)' : '1px solid var(--color-border)',
                borderRadius: '8px',
                padding: '0.875rem 1rem',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '0.5rem'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontWeight: 600, color: isSelected ? 'var(--color-accent-cyan)' : 'var(--color-text-main)', fontSize: '0.9375rem' }}>
                      {ind.name}
                    </span>
                    <span style={{
                      fontSize: '0.6875rem',
                      textTransform: 'uppercase',
                      padding: '0.1rem 0.35rem',
                      borderRadius: '4px',
                      background: 'rgba(255, 255, 255, 0.05)',
                      color: 'var(--color-text-muted)'
                    }}>
                      {ind.category}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-accent-amber)', marginTop: '0.125rem' }}>
                    {ind.desc}
                  </div>
                </div>

                <input 
                  type="checkbox" 
                  checked={isSelected}
                  onChange={() => {}}
                  style={{
                    accentColor: 'var(--color-accent-cyan)',
                    width: '16px',
                    height: '16px',
                    cursor: 'pointer',
                    marginTop: '2px'
                  }}
                />
              </div>

              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', lineHeight: 1.35, display: 'flex', gap: '0.375rem', alignItems: 'flex-start' }}>
                <Info size={13} style={{ flexShrink: 0, marginTop: '2px', opacity: 0.7 }} />
                <span>{ind.detail}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default StepIndicators;
