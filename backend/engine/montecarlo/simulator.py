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
    """Simulates alternate market paths through vectorized trade permutation and bootstrapping."""

    def __init__(self, n_simulations: int = 500, ruin_threshold: float = 0.5):
        self.n_simulations = min(1000, max(50, n_simulations))
        self.ruin_threshold = ruin_threshold

    def simulate(
        self,
        trade_pnls: list[float] | np.ndarray,
        initial_balance: float = 10000.0,
        n_simulations: int | None = None,
        method: str = "permutation"
    ) -> MonteCarloResult:
        n_sims = min(1000, max(50, n_simulations or self.n_simulations))
        trades = np.asarray(trade_pnls, dtype=np.float64)
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

        # Original curve
        orig_equity = [initial_balance]
        cum_orig = initial_balance + np.cumsum(trades)
        orig_equity.extend([float(x) for x in cum_orig])

        ruin_balance = initial_balance * (1.0 - self.ruin_threshold)

        # Fast Vectorized Monte Carlo Matrix
        if method == "bootstrap":
            sim_indices = np.random.randint(0, n_trades, size=(n_sims, n_trades))
            sim_trades = trades[sim_indices]
        else:
            sim_trades = np.tile(trades, (n_sims, 1))
            for row in sim_trades:
                np.random.shuffle(row)

        cum_matrix = initial_balance + np.cumsum(sim_trades, axis=1)  # shape (n_sims, n_trades)
        full_curves = np.column_stack([np.full(n_sims, initial_balance), cum_matrix])

        # Min balance & ruin
        min_balances = np.min(full_curves, axis=1)
        ruin_count = int(np.sum(min_balances <= ruin_balance))

        # Peak & Drawdowns vectorized
        peaks = np.maximum.accumulate(full_curves, axis=1)
        drawdowns = (peaks - full_curves) / (peaks + 1e-8)
        max_drawdowns = np.max(drawdowns, axis=1).tolist()
        final_balances = full_curves[:, -1].tolist()

        # Sharpe ratios
        returns = np.diff(full_curves, axis=1) / (full_curves[:, :-1] + 1e-8)
        means = np.mean(returns, axis=1)
        stds = np.std(returns, axis=1) + 1e-8
        sharpe_ratios = (means / stds).tolist()

        simulated_curves = [full_curves[k].tolist() for k in range(min(30, n_sims))]

        prob_ruin = float(ruin_count / n_sims)
        conf_95_dd = float(np.percentile(max_drawdowns, 95))
        pct_returns = [(b - initial_balance) / initial_balance for b in final_balances]
        conf_95_return = float(np.percentile(pct_returns, 5))

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
