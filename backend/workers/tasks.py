import uuid
import pandas as pd
from workers.celery_app import celery_app
from algoforge.supabase.client import get_supabase_client
from workers.callbacks import ProgressCallback
from workers.analysis_logger import AnalysisLogger
from engine.pipeline import StrategyPipeline, JobCancelledException
from algoforge.services.data_service import DataService
from algoforge.services.export_service import register_local_strategy

@celery_app.task(name="workers.tasks.run_strategy_pipeline", bind=True)
def run_strategy_pipeline(self, job_id: str, config: dict, user_id: str = ""):
    """Celery background worker task for running the AlgoForge strategy discovery pipeline."""
    client = get_supabase_client()
    cb = ProgressCallback(job_id, client)
    log = AnalysisLogger(job_id)

    log.section("Parámetros de entrada del job")
    log.config("symbol", (config.get("dataSource", {}) or {}).get("symbol", config.get("symbol", "?")))
    log.config("timeframe", (config.get("dataSource", {}) or {}).get("timeframe", config.get("timeframe", "?")))
    log.config("indicadores", config.get("indicators", []))
    log.config("tpslModes", config.get("tpslModes", []))
    log.config("genetic", config.get("genetic", {}))

    cb.update(5, "Fetching OHLCV historical data", phase="queued")
    
    try:
        data_svc = DataService()
        data_cfg = config.get("dataSource", {})
        symbol = data_cfg.get("symbol", config.get("symbol", "BTC-USD"))
        timeframe = data_cfg.get("timeframe", config.get("timeframe", "1d"))
        start_date = data_cfg.get("startDate", data_cfg.get("start_date", config.get("start_date", "2023-01-01")))
        end_date = data_cfg.get("endDate", data_cfg.get("end_date", config.get("end_date", "2024-01-01")))
        source = data_cfg.get("source", config.get("data_source", "yfinance"))

        log.section("Descarga de datos")
        log.config("fuente", source)
        log.config("rango", f"{start_date} -> {end_date}")

        df = data_svc.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            start=start_date,
            end=end_date,
            source=source
        )
        log.config("barras descargadas", len(df))

        def progress_reporter(phase="indicators", progress=0, message="", **kwargs):
            cb.update(progress, message or f"Processing {phase}", phase=phase)
            log.info(f"[{phase}] {message or 'procesando'} (progress={progress}%)")

        config["id"] = job_id
        config["job_id"] = job_id
        pipeline = StrategyPipeline(config, logger=log)
        ranked_strategies = pipeline.run(df, progress_callback=progress_reporter)

        # Check if cancelled during or after pipeline run
        if cb.is_cancelled():
            cb.update(100, "Análisis cancelado por el usuario", phase="cancelled", status="cancelled")
            log.close("cancelled")
            return {"status": "cancelled", "strategies_count": 0}

        # Save strategies to Supabase & local registry (guaranteeing valid UUIDs)
        for strat in ranked_strategies:
            strat["job_id"] = job_id
            strat["user_id"] = user_id

            # Ensure valid PostgreSQL UUID primary key
            raw_id = strat.get("id")
            try:
                strat_uuid = str(uuid.UUID(str(raw_id)))
            except Exception:
                strat_uuid = str(uuid.uuid4())

            strat["id"] = strat_uuid

            register_local_strategy(strat)

            exit_rules_payload = dict(strat.get("exit_rules", {}))
            exit_rules_payload["risk_config"] = strat.get("risk_config") or config.get("risk", {})
            exit_rules_payload["detailed_metrics"] = {
                "gross_profit": strat.get("gross_profit", 0.0),
                "gross_loss": strat.get("gross_loss", 0.0),
                "expected_payoff": strat.get("expected_payoff", 0.0),
                "consecutive_wins_max": strat.get("consecutive_wins_max", 0),
                "consecutive_wins_max_cash": strat.get("consecutive_wins_max_cash", 0.0),
                "consecutive_losses_max": strat.get("consecutive_losses_max", 0),
                "consecutive_losses_max_cash": strat.get("consecutive_losses_max_cash", 0.0),
                "consecutive_wins_avg": strat.get("consecutive_wins_avg", 0.0),
                "consecutive_losses_avg": strat.get("consecutive_losses_avg", 0.0),
                "recovery_factor": strat.get("recovery_factor", 0.0)
            }

            strat_record = {
                "id": strat_uuid,
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
                "exit_rules": exit_rules_payload,
                "equity_curve": strat.get("equity_curve", []),
                "trade_log": strat.get("trade_log", [])
            }
            try:
                client.table("strategies").upsert(strat_record).execute()
            except Exception as insert_err:
                print(f"[Strategy DB insert notice]: {insert_err}")

        cb.update(100, "Completed", phase="done", status="completed")
        log.section("Guardado de resultados")
        log.config("estrategias guardadas", len(ranked_strategies))
        log.close("completed")
        return {"status": "success", "strategies_count": len(ranked_strategies)}

    except JobCancelledException as e:
        print(f"[Job cancelled]: {e}")
        cb.update(100, "Análisis cancelado por el usuario", phase="cancelled", status="cancelled")
        log.close("cancelled")
        return {"status": "cancelled", "message": str(e)}

    except Exception as e:
        print(f"[Pipeline execution error]: {e}")
        cb.update(100, f"Failed: {str(e)}", phase="failed", status="failed")
        log.close(f"failed: {e}")
        return {"status": "failed", "error": str(e)}

