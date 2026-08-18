import pandas as pd
import numpy as np
from .indicators.calculator import IndicatorCalculator
from .genetic.evolution import StrategyEvolver
from .reinforcement.trainer import RLTrainer
from .backtester.vectorbt_engine import VectorBTEngine
from .montecarlo.simulator import MonteCarloSimulator
from .ranker.scoring import StrategyRanker

class StrategyPipeline:
    """End-to-end algorithmic strategy discovery, validation and ranking pipeline matching MT5."""

    def __init__(self, config: dict):
        self.config = config
        self.job_id = config.get("id") or config.get("job_id") or "default_job"
        self.risk_config = config.get("risk", {
            "initialDeposit": 10000.0,
            "sizingMode": "lots",
            "lotSize": 0.1,
            "riskPct": 1.0,
            "slType": "pips",
            "slPips": 50.0,
            "slAtrMult": 1.5,
            "tpType": "pips",
            "tpPips": 100.0,
            "tpAtrMult": 3.0,
            "contractSize": 100000.0,
            "pointSize": 0.0001,
            "spreadPips": 1.0,
            "commissionPerLot": 7.0,
            "commissionPerSide": True,
            "swapPerLotPerDay": 0.0
        })
        self.calculator = IndicatorCalculator()
        self.backtester = VectorBTEngine(self.risk_config)
        self.mc = MonteCarloSimulator(
            n_simulations=config.get("montecarlo", {}).get("simulations", 1000),
            ruin_threshold=config.get("montecarlo", {}).get("ruinThreshold", 50) / 100.0
        )
        self.ranker = StrategyRanker()

    def run(self, df: pd.DataFrame, progress_callback=None) -> list[dict]:
        """Execute the full discovery pipeline and return top ranked strategies."""
        # 1. Indicator Calculation
        if progress_callback:
            progress_callback(phase="indicators", progress=10, message="Calculating technical indicators")

        selected_inds = self.config.get("indicators", ["RSI", "MACD", "EMA", "SMA"])
        ind_params = self.config.get("indicatorParams", {})
        
        ind_configs = []
        import random
        for ind in selected_inds:
            # 1. Add the default indicator configuration
            default_p = ind_params.get(ind, {})
            ind_configs.append({"name": ind, "params": default_p, "var_name": ind})
            
            # 2. Add 3 random variations to enrich the genetic search space
            for v in range(1, 4):
                var_p = default_p.copy()
                # Simple mutation strategy for standard periods (usually named window, period, length)
                for p_key, p_val in var_p.items():
                    if isinstance(p_val, int) and p_val > 0:
                        var_p[p_key] = max(1, p_val + random.randint(-int(p_val*0.5), int(p_val*0.5)))
                    elif isinstance(p_val, float):
                        var_p[p_key] = p_val * random.uniform(0.5, 1.5)
                
                ind_configs.append({"name": ind, "params": var_p, "var_name": f"{ind}_v{v}"})
        
        indicators = self.calculator.calculate_all(df, ind_configs)
        
        # Save parameter map for the exporter
        self.ind_param_map = {cfg["var_name"]: cfg["params"] for cfg in ind_configs}

        # 2. Genetic Evolution
        if progress_callback:
            progress_callback(phase="genetic", progress=25, message="Evolving strategy population")

        gen_cfg = self.config.get("genetic", {})
        top_target = int(gen_cfg.get("topStrategiesCount") or self.config.get("topStrategiesCount") or 20)
        evolver = StrategyEvolver(
            ohlcv_data=df,
            indicator_values=indicators,
            population_size=gen_cfg.get("populationSize", 100),
            n_generations=gen_cfg.get("generations", 25),
            crossover_prob=gen_cfg.get("crossoverProb", 0.7),
            mutation_prob=gen_cfg.get("mutationProb", 0.1),
            risk_config=self.risk_config,
            top_strategies_count=top_target
        )

        gp_strategies = evolver.evolve(
            progress_callback=lambda **kwargs: progress_callback(
                phase="genetic",
                progress=25 + int(kwargs.get("progress", 0) * 0.25),
                message=f"Generation {kwargs.get('generation', 0)}/{kwargs.get('total_generations', 0)}"
            ) if progress_callback else None
        )

        # 3. RL Agent (if enabled)
        rl_cfg = self.config.get("rl", {})
        if rl_cfg.get("enabled", False):
            if progress_callback:
                progress_callback(phase="rl", progress=55, message="Training RL trading agent & Exporting ONNX")
            trainer = RLTrainer(
                algorithm=rl_cfg.get("algorithm", "ppo"),
                total_timesteps=rl_cfg.get("timesteps", 10000),
                learning_rate=rl_cfg.get("learningRate", 0.0003)
            )
            _, rl_info = trainer.train(
                df=df,
                indicators=indicators,
                job_id=self.job_id,
                strategy_id=f"rl_{rl_cfg.get('algorithm', 'ppo')}"
            )
            bt_rl = self.backtester.backtest(df, rl_info["entries"], rl_info["exits"])
            gp_strategies.append({
                "id": f"rl_agent_{rl_cfg.get('algorithm', 'ppo')}",
                "tree": f"RL_Agent({rl_cfg.get('algorithm', 'ppo').upper()})",
                "fitness": bt_rl.sharpe_ratio,
                "entries": rl_info["entries"],
                "exits": rl_info["exits"],
                "backtest": bt_rl,
                "is_rl": True,
                "onnx_filename": rl_info.get("onnx_filename"),
                "onnx_path": rl_info.get("onnx_path"),
                "zip_path": rl_info.get("zip_path"),
                "window_size": rl_info.get("window_size", 20),
                "n_features": rl_info.get("n_features", 5 + len(indicators))
            })

        # 4. Backtesting & Monte Carlo Validation
        if progress_callback:
            progress_callback(phase="backtest", progress=75, message="Validating performance & robustness")

        atr_arr = indicators.get("ATR")
        candidate_results = []
        for i, strat in enumerate(gp_strategies):
            bt = strat.get("backtest")
            if bt is None or bt.n_trades == 0:
                bt = self.backtester.backtest(df, strat["entries"], strat["exits"], atr_array=atr_arr)

            # Monte Carlo
            mc_method = self.config.get("montecarlo", {}).get("method", "permutation")
            mc_res = self.mc.simulate(bt.trade_pnls, method=mc_method)

            candidate_results.append({
                "id": strat["id"],
                "strategy_tree": strat["tree"],
                "is_rl": strat.get("is_rl", False),
                "job_id": self.job_id,
                "indicator_config": self.ind_param_map,
                "onnx_filename": strat.get("onnx_filename", f"AlgoForge_Job_{self.job_id}.onnx"),
                "onnx_path": strat.get("onnx_path", ""),
                "zip_path": strat.get("zip_path", ""),
                "window_size": strat.get("window_size", 20),
                "n_features": strat.get("n_features", 5),
                "total_return_pct": float(bt.total_return),
                "total_net_profit": float(bt.total_net_profit),
                "gross_profit": float(bt.gross_profit),
                "gross_loss": float(bt.gross_loss),
                "expected_payoff": float(bt.expected_payoff),
                "sharpe_ratio": float(bt.sharpe_ratio) if not np.isnan(bt.sharpe_ratio) else 0.0,
                "max_drawdown_pct": float(bt.max_drawdown) if not np.isnan(bt.max_drawdown) else 0.0,
                "win_rate": float(bt.win_rate) if not np.isnan(bt.win_rate) else 0.0,
                "profit_factor": float(bt.profit_factor) if not np.isnan(bt.profit_factor) else 0.0,
                "n_trades": int(bt.n_trades),
                "consecutive_wins_max": int(bt.consecutive_wins_max),
                "consecutive_wins_max_cash": float(bt.consecutive_wins_max_cash),
                "consecutive_losses_max": int(bt.consecutive_losses_max),
                "consecutive_losses_max_cash": float(bt.consecutive_losses_max_cash),
                "consecutive_wins_avg": float(bt.consecutive_wins_avg),
                "consecutive_losses_avg": float(bt.consecutive_losses_avg),
                "recovery_factor": float(bt.recovery_factor),
                "mc_robustness": float(mc_res.robustness_score),
                "mc_prob_ruin": float(mc_res.probability_of_ruin),
                "mc_95_drawdown": float(mc_res.confidence_95_drawdown),
                "equity_curve": bt.equity_curve,
                "trade_log": bt.trade_log,
                "indicator_config": ind_configs,
                "risk_config": self.risk_config,
                "entry_rules": {"tree": strat["tree"]},
                "exit_rules": {"rule": "sl_tp_or_signal"}
            })

        # 5. Ranking
        if progress_callback:
            progress_callback(phase="ranking", progress=90, message="Compiling strategy ranking")

        ranked_strategies = self.ranker.rank(candidate_results)[:top_target]

        if progress_callback:
            progress_callback(phase="done", progress=100, message="Pipeline complete")

        return ranked_strategies
