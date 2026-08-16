import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from .mt5_simulator import MT5TradeSimulator, MT5SimulationResult

@dataclass
class BacktestResult:
    total_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    n_trades: int = 0
    trade_pnls: list[float] = field(default_factory=list)
    equity_curve: list[float] = field(default_factory=list)
    # MT5 Detailed Metrics
    total_net_profit: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    expected_payoff: float = 0.0
    consecutive_wins_max: int = 0
    consecutive_wins_max_cash: float = 0.0
    consecutive_losses_max: int = 0
    consecutive_losses_max_cash: float = 0.0
    consecutive_wins_avg: float = 0.0
    consecutive_losses_avg: float = 0.0
    recovery_factor: float = 0.0
    trade_log: list[dict] = field(default_factory=list)

class VectorBTEngine:
    """High-speed portfolio backtester matching MT5 execution logic."""

    def __init__(self, risk_config: dict | None = None):
        self.risk_config = risk_config or {}
        self.simulator = MT5TradeSimulator(self.risk_config)

    def backtest(
        self,
        df: pd.DataFrame,
        entry_signals: np.ndarray | pd.Series | list[bool],
        exit_signals: np.ndarray | pd.Series | list[bool],
        atr_array: np.ndarray | None = None,
        initial_cash: float | None = None
    ) -> BacktestResult:
        if initial_cash:
            self.simulator.initial_deposit = initial_cash

        sim_res = self.simulator.simulate(
            df=df,
            buy_signals=np.asarray(entry_signals, dtype=bool),
            sell_signals=np.asarray(exit_signals, dtype=bool),
            atr_array=atr_array
        )

        return BacktestResult(
            total_return=sim_res.total_return_pct,
            sharpe_ratio=sim_res.sharpe_ratio,
            max_drawdown=sim_res.max_drawdown_pct,
            win_rate=sim_res.win_rate,
            profit_factor=sim_res.profit_factor,
            n_trades=sim_res.total_trades,
            trade_pnls=sim_res.trade_pnls,
            equity_curve=sim_res.equity_curve,
            total_net_profit=sim_res.total_net_profit,
            gross_profit=sim_res.gross_profit,
            gross_loss=sim_res.gross_loss,
            expected_payoff=sim_res.expected_payoff,
            consecutive_wins_max=sim_res.consecutive_wins_max,
            consecutive_wins_max_cash=sim_res.consecutive_wins_max_cash,
            consecutive_losses_max=sim_res.consecutive_losses_max,
            consecutive_losses_max_cash=sim_res.consecutive_losses_max_cash,
            consecutive_wins_avg=sim_res.consecutive_wins_avg,
            consecutive_losses_avg=sim_res.consecutive_losses_avg,
            recovery_factor=sim_res.recovery_factor,
            trade_log=sim_res.trade_log
        )
