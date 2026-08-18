export interface Strategy {
  id: string
  job_id: string
  user_id: string
  rank: number
  total_score: number
  sharpe_ratio: number
  total_return_pct: number
  total_net_profit?: number
  gross_profit?: number
  gross_loss?: number
  expected_payoff?: number
  recovery_factor?: number
  max_drawdown_pct: number
  win_rate: number
  profit_factor: number
  n_trades: number
  consecutive_wins_max?: number
  consecutive_wins_max_cash?: number
  consecutive_losses_max?: number
  consecutive_losses_max_cash?: number
  consecutive_wins_avg?: number
  consecutive_losses_avg?: number
  mc_robustness: number
  mc_prob_ruin: number
  mc_95_drawdown: number
  strategy_tree: string
  indicator_config: Record<string, unknown>
  risk_config?: Record<string, unknown>
  entry_rules: Record<string, unknown>
  exit_rules: Record<string, unknown>
  equity_curve: number[]
  trade_log: TradeEntry[]
  created_at: string
}

export interface TradeEntry {
  trade_idx?: number
  entry_time?: string
  exit_time?: string
  direction: 'buy' | 'sell' | 'long' | 'short'
  entry_price: number
  exit_price: number
  sl_price?: number | null
  tp_price?: number | null
  size?: number
  pnl: number
  pnl_pct: number
  exit_reason?: string
  duration_bars?: number
}
