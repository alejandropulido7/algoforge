export type JobStatus = 'pending' | 'running' | 'completed' | 'failed'
export type JobPhase = 'queued' | 'indicators' | 'genetic' | 'rl' | 'backtest' | 'montecarlo' | 'ranking' | 'done'

export type TradeDirection = 'both' | 'long' | 'short'

export interface RiskConfig {
  initialDeposit: number
  sizingMode: 'lots' | 'risk_pct' | 'cash'
  lotSize: number
  riskPct: number
  direction: TradeDirection
  slType: 'pips' | 'atr' | 'none'
  slPips: number
  slAtrMult: number
  tpType: 'pips' | 'atr' | 'none'
  tpPips: number
  tpAtrMult: number
  contractSize: number
  pointSize: number
}

export interface JobConfig {
  dataSource: {
    source: 'yfinance' | 'csv'
    symbol: string
    timeframe: string
    startDate: string
    endDate: string
  }
  indicators: string[]
  indicatorParams: Record<string, Record<string, number>>
  risk: RiskConfig
  genetic: {
    populationSize: number
    generations: number
    crossoverProb: number
    mutationProb: number
  }
  rl: {
    enabled: boolean
    algorithm: 'ppo' | 'a2c'
    timesteps: number
    learningRate: number
  }
  montecarlo: {
    simulations: number
    method: 'permutation' | 'bootstrap'
    ruinThreshold: number
  }
}

export interface Job {
  id: string
  user_id: string
  status: JobStatus
  config: JobConfig
  progress: number
  current_phase: JobPhase
  created_at: string
  completed_at: string | null
  error_message: string | null
}
