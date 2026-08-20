import os
import pandas as pd
import numpy as np
import yfinance as yf
from engine.pipeline import StrategyPipeline
from workers.analysis_logger import AnalysisLogger

def run_e2e_test():
    print("=" * 70)
    print("INICIANDO PRUEBA END-TO-END DEL PIPELINE CON ESPACIO DE BÚSQUEDA")
    print("=" * 70)

    # 1. Fetch real market data
    symbol = "EURUSD=X"
    print(f"Descargando datos de mercado para {symbol}...")
    df = yf.download(symbol, start="2023-01-01", end="2024-01-01", interval="1d", progress=False)
    if df.empty or len(df) < 50:
        print("Fallback a dataset sintético...")
        dates = pd.date_range("2023-01-01", periods=200, freq="1d")
        np.random.seed(42)
        c = 1.08 + np.cumsum(np.random.randn(200) * 0.003)
        h = c + np.abs(np.random.randn(200) * 0.002)
        l = c - np.abs(np.random.randn(200) * 0.002)
        o = (h + l) / 2.0
        df = pd.DataFrame({"Open": o, "High": h, "Low": l, "Close": c, "Volume": [1000]*200}, index=dates)
    else:
        # Standardize MultiIndex columns if returned by yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

    print(f"Dataset cargado: {len(df)} barras OHLCV.")

    # 2. Configuración de prueba con 12 combinaciones exactas
    job_id = "job_e2e_test_grid_12"
    job_config = {
        "id": job_id,
        "dataSource": {
            "symbol": "EUR/USD",
            "timeframe": "1d",
            "startDate": "2023-01-01",
            "endDate": "2024-01-01"
        },
        "indicators": ["RSI", "EMA", "Bollinger"],
        "indicatorRanges": {
            "RSI": {
                "period": {"min": 10, "step": 2, "max": 14},       # [10, 12, 14] -> 3
                "oversold": {"min": 30, "step": 5, "max": 35},     # [30, 35] -> 2
                "overbought": {"min": 65, "step": 5, "max": 70}    # [65, 70] -> 2
                # Total RSI = 3 * 2 * 2 = 12
            },
            "EMA": {
                "period": {"min": 10, "step": 10, "max": 20}       # [10, 20] -> 2
            },
            "Bollinger": {
                "period": {"min": 20, "step": 10, "max": 20},      # [20] -> 1
                "deviation": {"min": 1.5, "step": 0.5, "max": 2.0} # [1.5, 2.0] -> 2
            }
        },
        # Total combinations esperadas = 12 * 2 * 2 = 48
        "tpslModes": ["atr_classic", "trailing_stop", "breakeven"],
        "tpslRanges": {
            "atr_classic": {
                "sl_atr": {"min": 1.5, "step": 0.5, "max": 1.5},
                "tp_atr": {"min": 3.0, "step": 0.5, "max": 3.0}
            },
            "trailing_stop": {
                "trail_atr": {"min": 1.0, "step": 0.5, "max": 1.0}
            },
            "breakeven": {
                "be_atr": {"min": 1.0, "step": 0.5, "max": 1.0}
            }
        },
        "risk": {
            "initialDeposit": 10000.0,
            "lotSize": 0.1,
            "direction": "both",
            "spreadPips": 1.0,
            "commissionPerLot": 7.0
        },
        "genetic": {
            "populationSize": 20,
            "generations": 2,
            "topStrategiesCount": 5
        },
        "montecarlo": {
            "simulations": 500,
            "method": "permutation",
            "ruinThreshold": 20
        }
    }

    log = AnalysisLogger(job_id)
    pipeline = StrategyPipeline(job_config, logger=log)

    def progress_cb(phase, progress, message):
        print(f"  [Progreso] {phase.upper()} ({progress}%): {message}")

    print("\nEjecutando Pipeline...")
    ranked_strategies = pipeline.run(df, progress_callback=progress_cb)

    print("\n" + "=" * 70)
    print(f"ANÁLISIS COMPLETADO: {len(ranked_strategies)} ESTRATEGIAS FINALISTAS RANKING")
    print("=" * 70)

    for s in ranked_strategies:
        print(f"\n★ Rank #{s['rank']} | Score: {s['total_score']} | ID: {s['id']}")
        print(f"  • Regla / Árbol: {s['strategy_tree']}")
        print(f"  • Retorno Total: {s['total_return_pct']:+.2f}% | Net Profit: ${s['total_net_profit']:,.2f}")
        print(f"  • Win Rate: {s['win_rate']:.1f}% | Trades: {s['n_trades']} | Profit Factor: {s['profit_factor']:.2f}")
        print(f"  • Sharpe Ratio: {s['sharpe_ratio']:.2f} | Max Drawdown: {s['max_drawdown_pct']:.2f}%")
        print(f"  • Robustez Monte Carlo: {s['mc_robustness']:.1f}% | Prob Ruina: {s['mc_prob_ruin']:.1f}%")

    log_path = log.path
    print(f"\nArchivo de Log guardado en: {log_path}")
    return log_path

if __name__ == "__main__":
    run_e2e_test()
