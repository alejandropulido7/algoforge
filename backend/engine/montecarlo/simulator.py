import numpy as np
from dataclasses import dataclass

@dataclass
class MonteCarloResult:
    original_equity: list[float]
    simulated_curves: list[list[float]]
    max_drawdowns: list[float]
    final_balances: list[float]
    sharpe_ratios: list[float]
    confidence_95_drawdown: float
    confidence_95_return: float
    probability_of_ruin: float
    robustness_score: float

class MonteCarloSimulator:
    """Simulates alternate market paths through trade permutation and bootstrapping."""

    def __init__(self, n_simulations: int = 1000, ruin_threshold: float = 0.5):
        self.n_simulations = n_simulations
        self.ruin_threshold = ruin_threshold

    def simulate(
        self,
        trade_pnls: list[float] | np.ndarray,
        initial_balance: float = 10000.0,
        n_simulations: int | None = None,
        method: str = "permutation"
    ) -> MonteCarloResult:
        n_sims = n_simulations or self.n_simulations
        trades = np.asarray(trade_pnls)
        n_trades = len(trades)

        if n_trades == 0:
            return MonteCarloResult(
                original_equity=[initial_balance],
                simulated_curves=[[initial_balance]],
                max_drawdowns=[0.0],
                final_balances=[initial_balance],
                sharpe_ratios=[0.0],
                confidence_95_drawdown=0.0,
                confidence_95_return=0.0,
                probability_of_ruin=0.0,
                robustness_score=0.0
            )

        simulated_curves = []
        max_drawdowns = []
        final_balances = []
        sharpe_ratios = []

        # Original curve
        orig_equity = [initial_balance]
        for pnl in trades:
            # Handle percentage pnl or absolute pnl
            if abs(pnl) < 2.0:
                orig_equity.append(orig_equity[-1] * (1.0 + pnl))
            else:
                orig_equity.append(orig_equity[-1] + pnl)

        ruin_balance = initial_balance * (1.0 - self.ruin_threshold)
        ruin_count = 0

        for _ in range(n_sims):
            if method == "bootstrap":
                shuffled = np.random.choice(trades, size=n_trades, replace=True)
            else:
                shuffled = np.random.permutation(trades)

            curve = [initial_balance]
            hit_ruin = False
            for pnl in shuffled:
                val = curve[-1] * (1.0 + pnl) if abs(pnl) < 2.0 else curve[-1] + pnl
                curve.append(max(0.0, val))
                if curve[-1] <= ruin_balance:
                    hit_ruin = True

            if hit_ruin:
                ruin_count += 1

            curve_arr = np.array(curve)
            peak = np.maximum.accumulate(curve_arr)
            dd = (peak - curve_arr) / (peak + 1e-8)
            max_dd = float(np.max(dd))

            # Returns for Sharpe
            rets = np.diff(curve_arr) / (curve_arr[:-1] + 1e-8)
            sh = float(np.mean(rets) / (np.std(rets) + 1e-8)) if len(rets) > 1 else 0.0

            max_drawdowns.append(max_dd)
            final_balances.append(float(curve[-1]))
            sharpe_ratios.append(sh)
            if len(simulated_curves) < 30:
                simulated_curves.append(curve)

        prob_ruin = float(ruin_count / n_sims)
        conf_95_dd = float(np.percentile(max_drawdowns, 95))
        pct_returns = [(b - initial_balance) / initial_balance for b in final_balances]
        conf_95_return = float(np.percentile(pct_returns, 5))

        # Robustness score: 0 to 100
        profitable_pct = sum(1 for b in final_balances if b > initial_balance) / n_sims
        robustness = (
            profitable_pct * 0.4 +
            max(0.0, 1.0 - conf_95_dd) * 0.3 +
            (1.0 - prob_ruin) * 0.3
        ) * 100.0

        return MonteCarloResult(
            original_equity=orig_equity,
            simulated_curves=simulated_curves,
            max_drawdowns=max_drawdowns,
            final_balances=final_balances,
            sharpe_ratios=sharpe_ratios,
            confidence_95_drawdown=conf_95_dd,
            confidence_95_return=conf_95_return,
            probability_of_ruin=prob_ruin,
            robustness_score=round(robustness, 2)
        )
