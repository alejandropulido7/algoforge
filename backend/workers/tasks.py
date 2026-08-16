import pandas as pd
from workers.celery_app import celery_app
from algoforge.supabase.client import get_supabase_client
from workers.callbacks import ProgressCallback
from engine.pipeline import StrategyPipeline
from algoforge.services.data_service import DataService

@celery_app.task(name="workers.tasks.run_strategy_pipeline", bind=True)
def run_strategy_pipeline(self, job_id: str, config: dict, user_id: str = ""):
    """Celery background worker task for running the AlgoForge strategy discovery pipeline."""
    client = get_supabase_client()
    cb = ProgressCallback(job_id, client)
    
    cb.update(5, "Fetching OHLCV historical data", phase="queued")
    
    try:
        data_svc = DataService()
        data_cfg = config.get("dataSource", {})
        symbol = data_cfg.get("symbol", config.get("symbol", "BTC-USD"))
        timeframe = data_cfg.get("timeframe", config.get("timeframe", "1d"))
        start_date = data_cfg.get("startDate", data_cfg.get("start_date", config.get("start_date", "2023-01-01")))
        end_date = data_cfg.get("endDate", data_cfg.get("end_date", config.get("end_date", "2024-01-01")))
        source = data_cfg.get("source", config.get("data_source", "yfinance"))

        df = data_svc.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            start=start_date,
            end=end_date,
            source=source
        )

        def progress_reporter(phase="genetic", progress=0, message="", **kwargs):
            cb.update(progress, message or f"Processing {phase}", phase=phase)

        pipeline = StrategyPipeline(config)
        ranked_strategies = pipeline.run(df, progress_callback=progress_reporter)

        # Save strategies to Supabase
        for strat in ranked_strategies:
            strat_record = {
                "job_id": job_id,
                "user_id": user_id,
                "rank": strat.get("rank", 1),
                "total_score": strat.get("total_score", 0.0),
                "sharpe_ratio": strat.get("sharpe_ratio", 0.0),
                "total_return_pct": strat.get("total_return_pct", 0.0),
                "max_drawdown_pct": strat.get("max_drawdown_pct", 0.0),
                "win_rate": strat.get("win_rate", 0.0),
                "profit_factor": strat.get("profit_factor", 0.0),
                "n_trades": strat.get("n_trades", 0),
                "mc_robustness": strat.get("mc_robustness", 0.0),
                "mc_prob_ruin": strat.get("mc_prob_ruin", 0.0),
                "mc_95_drawdown": strat.get("mc_95_drawdown", 0.0),
                "strategy_tree": strat.get("strategy_tree", ""),
                "indicator_config": strat.get("indicator_config", {}),
                "entry_rules": strat.get("entry_rules", {}),
                "exit_rules": strat.get("exit_rules", {}),
                "equity_curve": strat.get("equity_curve", []),
                "trade_log": strat.get("trade_log", [])
            }
            try:
                client.table("strategies").insert(strat_record).execute()
            except Exception as insert_err:
                print(f"[Strategy DB insert warning]: {insert_err}")

        cb.update(100, "Completed", phase="done", status="completed")
        return {"status": "success", "strategies_count": len(ranked_strategies)}

    except Exception as e:
        print(f"[Pipeline execution error]: {e}")
        cb.update(100, f"Failed: {str(e)}", phase="failed", status="failed")
        return {"status": "failed", "error": str(e)}
