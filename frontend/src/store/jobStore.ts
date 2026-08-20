import { create } from 'zustand';
import type { JobConfig, RiskConfig, ParamRangeConfig } from '../types/job';
import { getIndicatorCatalogItem } from '../data/indicatorsCatalog';

interface JobState {
  currentStep: number;
  config: JobConfig;
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  updateDataSource: (data: Partial<JobConfig['dataSource']>) => void;
  toggleIndicator: (indicatorName: string, selected: boolean) => void;
  updateIndicatorParams: (indicatorName: string, params: Record<string, number>) => void;
  setIndicatorParamRange: (indicatorId: string, paramKey: string, range: Partial<ParamRangeConfig>) => void;
  toggleTPSLMode: (modeId: string, selected?: boolean) => void;
  setTPSLParamRange: (modeId: string, paramKey: string, range: Partial<ParamRangeConfig>) => void;
  updateRisk: (data: Partial<RiskConfig>) => void;
  updateGenetic: (data: Partial<JobConfig['genetic']>) => void;
  updateRL: (data: Partial<JobConfig['rl']>) => void;
  updateMonteCarlo: (data: Partial<JobConfig['montecarlo']>) => void;
  resetConfig: () => void;
}

const defaultConfig: JobConfig = {
  dataSource: {
    source: 'yfinance',
    symbol: 'BTC-USD',
    timeframe: '1d',
    startDate: '2023-01-01',
    endDate: '2024-01-01',
  },
  indicators: ['RSI', 'Bollinger', 'EMA', 'MACD'],
  indicatorParams: {},
  indicatorRanges: {
    'RSI': {
      'period': { min: 5, step: 1, max: 30 },
      'oversold': { min: 20, step: 1, max: 35 },
      'overbought': { min: 65, step: 1, max: 80 }
    },
    'Bollinger': {
      'period': { min: 15, step: 1, max: 30 },
      'deviation': { min: 1.5, step: 0.1, max: 3.0 }
    },
    'EMA': {
      'period': { min: 5, step: 5, max: 200 }
    },
    'MACD': {
      'fast': { min: 8, step: 1, max: 16 },
      'slow': { min: 20, step: 1, max: 35 },
      'signal': { min: 7, step: 1, max: 12 }
    }
  },
  tpslModes: [
    'atr_classic',
    'trailing_stop',
    'swing_structure',
    'time_exit',
    'percentage',
    'partial_tp',
    'breakeven',
    'fixed_pips',
    'smoothed_atr'
  ],
  tpslRanges: {
    'atr_classic': {
      'sl_atr': { min: 0.5, step: 0.1, max: 3.0 },
      'tp_atr': { min: 0.5, step: 0.1, max: 6.0 }
    },
    'trailing_stop': {
      'trail_atr': { min: 0.5, step: 0.1, max: 2.5 }
    },
    'swing_structure': {
      'lookback': { min: 10, step: 5, max: 50 }
    },
    'time_exit': {
      'max_bars': { min: 5, step: 1, max: 12 }
    },
    'percentage': {
      'sl_pct': { min: 0.2, step: 0.1, max: 2.0 },
      'tp_pct': { min: 0.5, step: 0.1, max: 4.0 }
    },
    'partial_tp': {
      'tp1_atr': { min: 0.5, step: 0.1, max: 2.0 },
      'tp2_atr': { min: 2.0, step: 0.1, max: 6.0 },
      'close_pct': { min: 30, step: 10, max: 70 }
    },
    'breakeven': {
      'be_atr': { min: 0.5, step: 0.1, max: 2.0 }
    },
    'fixed_pips': {
      'sl_pips': { min: 10, step: 5, max: 50 },
      'tp_pips': { min: 20, step: 5, max: 100 }
    },
    'smoothed_atr': {
      'sl_atr_smooth': { min: 0.5, step: 0.1, max: 3.0 },
      'tp_atr_smooth': { min: 1.0, step: 0.1, max: 6.0 }
    }
  },
  risk: {
    direction: 'both',
    orderType: 'market',
    maxSimultaneousTrades: 1,
    consecutiveLossAction: 'none',
    consecutiveLossThreshold: 3,
    consecutiveLossReductionPct: 50,
    consecutiveLossReactivation: 'none',
    consecutiveLossCooldownBars: 20,
    consecutiveLossCooldownDays: 1,
    consecutiveLossAutoCooldown: true,
    contractSize: 100000,
    pointSize: 0.0001,
    spreadPips: 1.0,
    commissionPerLot: 7.0,
    commissionPerSide: true,
    swapPerLotPerDay: 0.0,
    initialDeposit: 10000,
    sizingMode: 'lots',
    lotSize: 0.1,
    riskPct: 1.0,
    riskBase: 'initial_deposit',
    slType: 'none',
    slPips: 50.0,
    slAtrMult: 1.5,
    tpType: 'none',
    tpPips: 100.0,
    tpAtrMult: 3.0,
  },
  genetic: {
    populationSize: 187,
    generations: 35,
    crossoverProb: 0.7,
    mutationProb: 0.1,
    topStrategiesCount: 20,
  },
  rl: {
    enabled: false,
    algorithm: 'ppo',
    timesteps: 100000,
    learningRate: 0.0003,
  },
  montecarlo: {
    simulations: 1000,
    method: 'permutation',
    ruinThreshold: 20,
  },
};

export const useJobStore = create<JobState>((set) => ({
  currentStep: 1,
  config: defaultConfig,
  setStep: (step) => set({ currentStep: step }),
  nextStep: () => set((state) => ({ currentStep: Math.min(state.currentStep + 1, 5) })),
  prevStep: () => set((state) => ({ currentStep: Math.max(state.currentStep - 1, 1) })),
  updateDataSource: (data) => set((state) => ({ config: { ...state.config, dataSource: { ...state.config.dataSource, ...data } } })),
  toggleIndicator: (indicatorName, selected) => set((state) => {
    const indicators = selected
      ? (state.config.indicators.includes(indicatorName) ? state.config.indicators : [...state.config.indicators, indicatorName])
      : state.config.indicators.filter((i) => i !== indicatorName);
    
    let newRanges = { ...(state.config.indicatorRanges || {}) };
    if (selected && !newRanges[indicatorName]) {
      const item = getIndicatorCatalogItem(indicatorName);
      if (item && item.params.length > 0) {
        const itemRanges: Record<string, ParamRangeConfig> = {};
        for (const p of item.params) {
          itemRanges[p.key] = { min: p.defaultMin, step: p.defaultStep, max: p.defaultMax };
        }
        newRanges[indicatorName] = itemRanges;
      }
    }

    return { config: { ...state.config, indicators, indicatorRanges: newRanges } };
  }),
  updateIndicatorParams: (indicatorName, params) => set((state) => ({
    config: {
      ...state.config,
      indicatorParams: { ...state.config.indicatorParams, [indicatorName]: params }
    }
  })),
  setIndicatorParamRange: (indicatorId, paramKey, range) => set((state) => {
    const prevRanges = state.config.indicatorRanges || {};
    const prevIndRanges = prevRanges[indicatorId] || {};
    const currentParamRange = prevIndRanges[paramKey] || { min: 1, step: 1, max: 10 };
    return {
      config: {
        ...state.config,
        indicatorRanges: {
          ...prevRanges,
          [indicatorId]: {
            ...prevIndRanges,
            [paramKey]: { ...currentParamRange, ...range }
          }
        }
      }
    };
  }),
  toggleTPSLMode: (modeId, selected) => set((state) => {
    const currentModes = state.config.tpslModes || [];
    const isCurrentlySelected = currentModes.includes(modeId);
    const shouldSelect = selected !== undefined ? selected : !isCurrentlySelected;
    const newModes = shouldSelect
      ? (isCurrentlySelected ? currentModes : [...currentModes, modeId])
      : currentModes.filter(m => m !== modeId);
    return {
      config: {
        ...state.config,
        tpslModes: newModes
      }
    };
  }),
  setTPSLParamRange: (modeId, paramKey, range) => set((state) => {
    const prevRanges = state.config.tpslRanges || {};
    const prevModeRanges = prevRanges[modeId] || {};
    const currentParamRange = prevModeRanges[paramKey] || { min: 0.5, step: 0.1, max: 3.0 };
    return {
      config: {
        ...state.config,
        tpslRanges: {
          ...prevRanges,
          [modeId]: {
            ...prevModeRanges,
            [paramKey]: { ...currentParamRange, ...range }
          }
        }
      }
    };
  }),
  updateRisk: (data) => set((state) => ({ config: { ...state.config, risk: { ...state.config.risk, ...data } } })),
  updateGenetic: (data) => set((state) => ({ config: { ...state.config, genetic: { ...state.config.genetic, ...data } } })),
  updateRL: (data) => set((state) => ({ config: { ...state.config, rl: { ...state.config.rl, ...data } } })),
  updateMonteCarlo: (data) => set((state) => ({ config: { ...state.config, montecarlo: { ...state.config.montecarlo, ...data } } })),
  resetConfig: () => set({ currentStep: 1, config: defaultConfig }),
}));
