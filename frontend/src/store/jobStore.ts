import { create } from 'zustand';
import type { JobConfig, RiskConfig } from '../types/job';

interface JobState {
  currentStep: number;
  config: JobConfig;
  setStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  updateDataSource: (data: Partial<JobConfig['dataSource']>) => void;
  toggleIndicator: (indicatorName: string, selected: boolean) => void;
  updateIndicatorParams: (indicatorName: string, params: Record<string, number>) => void;
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
  indicators: ['RSI', 'EMA'],
  indicatorParams: {},
  risk: {
    initialDeposit: 10000,
    sizingMode: 'lots',
    lotSize: 0.1,
    riskPct: 1.0,
    direction: 'both',
    strategyApproach: 'all',
    orderType: 'market',
    pendingTimeoutBars: 3,
    pendingOffsetPips: 5.0,
    maxHoldingBars: 0,
    consecutiveLossAction: 'none',
    consecutiveLossThreshold: 3,
    consecutiveLossReductionPct: 50,
    consecutiveLossReactivation: 'none',
    consecutiveLossCooldownBars: 20,
    consecutiveLossCooldownDays: 1,
    consecutiveLossAutoCooldown: true,
    slType: 'pips',
    slPips: 50.0,
    slAtrMult: 1.5,
    tpType: 'pips',
    tpPips: 100.0,
    tpAtrMult: 3.0,
    contractSize: 100000,
    pointSize: 0.0001,
  },
  genetic: {
    populationSize: 100,
    generations: 50,
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
      ? [...state.config.indicators, indicatorName]
      : state.config.indicators.filter((i) => i !== indicatorName);
    return { config: { ...state.config, indicators } };
  }),
  updateIndicatorParams: (indicatorName, params) => set((state) => ({
    config: {
      ...state.config,
      indicatorParams: { ...state.config.indicatorParams, [indicatorName]: params }
    }
  })),
  updateRisk: (data) => set((state) => ({ config: { ...state.config, risk: { ...state.config.risk, ...data } } })),
  updateGenetic: (data) => set((state) => ({ config: { ...state.config, genetic: { ...state.config.genetic, ...data } } })),
  updateRL: (data) => set((state) => ({ config: { ...state.config, rl: { ...state.config.rl, ...data } } })),
  updateMonteCarlo: (data) => set((state) => ({ config: { ...state.config, montecarlo: { ...state.config.montecarlo, ...data } } })),
  resetConfig: () => set({ currentStep: 1, config: defaultConfig }),
}));
