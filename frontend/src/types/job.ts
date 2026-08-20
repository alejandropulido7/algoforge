export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
export type JobPhase = 'queued' | 'indicators' | 'genetic' | 'rl' | 'backtest' | 'montecarlo' | 'ranking' | 'done' | 'cancelled'

export type TradeDirection = 'both' | 'long' | 'short'
export type OrderType = 'market' | 'stop' | 'limit' | 'any'
export type ConsecutiveLossAction = 'none' | 'reduce_risk' | 'stop_bot'
export type ConsecutiveLossReactivation = 'none' | 'cooldown_bars' | 'next_session' | 'next_day' | 'days_count' | 'next_week'

export interface RiskConfig {
  direction: TradeDirection
  orderType: OrderType
  maxSimultaneousTrades: number
  consecutiveLossAction: ConsecutiveLossAction
  consecutiveLossThreshold: number
  consecutiveLossReductionPct: number
  consecutiveLossReactivation: ConsecutiveLossReactivation
  consecutiveLossCooldownBars: number
  consecutiveLossCooldownDays: number
  consecutiveLossAutoCooldown: boolean
  contractSize: number
  pointSize: number
  spreadPips: number
  commissionPerLot: number
  commissionPerSide: boolean
  swapPerLotPerDay: number
  tpslModes?: string[]
  tpslRanges?: Record<string, Record<string, ParamRangeConfig>>
  // Optional / legacy fallback fields
  initialDeposit?: number
  sizingMode?: 'lots' | 'risk_pct' | 'cash'
  lotSize?: number
  riskPct?: number
  riskBase?: 'initial_deposit' | 'balance'
  slType?: 'pips' | 'atr' | 'none'
  slPips?: number
  slAtrMult?: number
  tpType?: 'pips' | 'atr' | 'none'
  tpPips?: number
  tpAtrMult?: number
  strategyApproach?: string
  pendingTimeoutBars?: number
  pendingOffsetPips?: number
  maxHoldingBars?: number
}

export interface ParamRangeConfig {
  min: number
  step: number
  max: number
}

export interface JobConfig {
  dataSource: {
    source: 'yfinance' | 'dukascopy' | 'csv' | 'mt5_csv' | string
    symbol: string
    timeframe: string
    startDate: string
    endDate: string
  }
  indicators: string[]
  indicatorParams: Record<string, Record<string, number>>
  indicatorRanges?: Record<string, Record<string, ParamRangeConfig>>
  tpslModes?: string[]
  tpslRanges?: Record<string, Record<string, ParamRangeConfig>>
  risk: RiskConfig
  genetic: {
    populationSize: number
    generations: number
    crossoverProb: number
    mutationProb: number
    topStrategiesCount: number
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
