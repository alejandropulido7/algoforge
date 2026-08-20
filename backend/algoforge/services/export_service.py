import os
from engine.exporters.mt5_exporter import MT5Exporter
from engine.exporters.pine_exporter import PineScriptExporter
from engine.exporters.onnx_mt5_exporter import OnnxMT5Exporter
from engine.exporters.python_live_exporter import PythonLiveExporter
from engine.exporters.indicators_exporter import CustomIndicatorsExporter
from algoforge.supabase.client import get_supabase_client

# Local cache for exported models
_LOCAL_STRATEGIES: dict[str, dict] = {}

def export_all_indicators():
    try:
        exporter = CustomIndicatorsExporter()
        return exporter.get_zip_buffer()
    except Exception as e:
        print(f"Error exporting indicators: {e}")
        return None

def register_local_strategy(strategy: dict):
    if "id" in strategy:
        _LOCAL_STRATEGIES[strategy["id"]] = strategy

def purge_local_strategies_by_job(job_id: str):
    keys_to_remove = [k for k, v in _LOCAL_STRATEGIES.items() if v.get("job_id") == job_id]
    for k in keys_to_remove:
        _LOCAL_STRATEGIES.pop(k, None)

def get_strategy_by_id(strategy_id: str) -> dict:
    client = get_supabase_client()
    strat: dict | None = None
    try:
        res = client.table("strategies").select("*").eq("id", strategy_id).single().execute()
        if res.data:
            strat = dict(res.data)
    except Exception:
        pass

    if not strat:
        strat = dict(_LOCAL_STRATEGIES.get(strategy_id, {
            "id": strategy_id,
            "rank": 1,
            "total_score": 50.0,
            "sharpe_ratio": 1.0,
            "mc_robustness": 80.0,
            "strategy_tree": "gt(RSI, c_50)",
            "is_rl": False
        }))

    # Enrich strategy with parent job configuration (Risk, Indicators, Monte Carlo, Symbol/Timeframe)
    job_id = strat.get("job_id")
    if job_id:
        try:
            from algoforge.services.job_service import get_job_status
            job_record = get_job_status(job_id)
            if job_record and "config" in job_record:
                job_cfg = job_record.get("config", {})

                # 1. Enrich risk_config. PRIORITY: the risk_config that was
                # actually applied during the backtest (stored in
                # exit_rules.risk_config by the pipeline) over the raw job
                # risk, so TP/SL Management (e.g. ATR Clásico) is reflected in
                # the strategy results instead of the un-sampled job defaults.
                applied_risk = {}
                er_risk = strat.get("exit_rules", {}).get("risk_config") if isinstance(strat.get("exit_rules"), dict) else None
                if isinstance(er_risk, dict):
                    applied_risk = er_risk
                if not strat.get("risk_config") or strat.get("risk_config") == {}:
                    if applied_risk:
                        strat["risk_config"] = applied_risk
                    elif "risk" in job_cfg and job_cfg["risk"]:
                        strat["risk_config"] = job_cfg["risk"]
                elif applied_risk and not strat.get("risk_config", {}).get("slType"):
                    # Strategy record has some risk but the applied one carries
                    # the effective SL/TP mode -> surface it.
                    merged = dict(strat["risk_config"])
                    merged.update({k: v for k, v in applied_risk.items() if v is not None})
                    strat["risk_config"] = merged

                # 2. Enrich indicator_config / indicatorParams
                if not strat.get("indicator_config") or strat.get("indicator_config") == {}:
                    ind_params = job_cfg.get("indicatorParams", {})
                    inds = job_cfg.get("indicators", [])
                    strat["indicator_config"] = [{"name": ind, "params": ind_params.get(ind, {})} for ind in inds]

                # 3. Enrich symbol / timeframe / montecarlo
                data_src = job_cfg.get("dataSource", {})
                if not strat.get("symbol"):
                    strat["symbol"] = data_src.get("symbol") or job_cfg.get("symbol") or "EURUSD"
                if not strat.get("timeframe"):
                    strat["timeframe"] = data_src.get("timeframe") or job_cfg.get("timeframe") or "H1"
                strat["montecarlo_config"] = job_cfg.get("montecarlo", {})
        except Exception as err:
            print(f"[get_strategy_by_id job enrichment notice]: {err}")

    # Fallback risk_config if still missing
    if not strat.get("risk_config") or strat.get("risk_config") == {}:
        if "risk_config" in strat.get("exit_rules", {}):
            strat["risk_config"] = strat["exit_rules"]["risk_config"]

    return strat

def export_strategy(strategy_id: str, format_type: str) -> str:
    strategy = get_strategy_by_id(strategy_id)
    is_rl = strategy.get("is_rl", False) or "RL_Agent" in str(strategy.get("strategy_tree", ""))

    if format_type == "mt5":
        if is_rl:
            return OnnxMT5Exporter().export(strategy)
        return MT5Exporter().export(strategy)
    elif format_type == "pine":
        return PineScriptExporter().export(strategy)
    elif format_type == "python":
        return PythonLiveExporter().export(strategy)
    return ""

def get_onnx_filepath(target_id: str) -> str | None:
    """Resolve ONNX filepath by either strategy_id or job_id."""
    models_dir = os.path.join(os.getcwd(), "models")
    
    # 1. Direct Job-level model check
    job_direct_path = os.path.join(models_dir, f"AlgoForge_Job_{target_id}.onnx")
    if os.path.exists(job_direct_path):
        return job_direct_path

    # 2. Check strategy record
    strategy = get_strategy_by_id(target_id)
    job_id = strategy.get("job_id", "")
    onnx_filename = strategy.get("onnx_filename", f"AlgoForge_Job_{job_id}.onnx" if job_id else f"{target_id}.onnx")
    
    possible_paths = [
        os.path.join(models_dir, onnx_filename),
        os.path.join(models_dir, f"AlgoForge_Job_{job_id}.onnx") if job_id else None,
        os.path.join(models_dir, f"{target_id}.onnx"),
        strategy.get("onnx_path", "")
    ]
    for p in possible_paths:
        if p and os.path.exists(p):
            return p
    return None
