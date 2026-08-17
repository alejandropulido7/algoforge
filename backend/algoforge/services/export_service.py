import os
from engine.exporters.mt5_exporter import MT5Exporter
from engine.exporters.pine_exporter import PineScriptExporter
from engine.exporters.onnx_mt5_exporter import OnnxMT5Exporter
from engine.exporters.python_live_exporter import PythonLiveExporter
from algoforge.supabase.client import get_supabase_client

# Local cache for exported models
_LOCAL_STRATEGIES: dict[str, dict] = {}

def register_local_strategy(strategy: dict):
    if "id" in strategy:
        _LOCAL_STRATEGIES[strategy["id"]] = strategy

def get_strategy_by_id(strategy_id: str) -> dict:
    client = get_supabase_client()
    try:
        res = client.table("strategies").select("*").eq("id", strategy_id).single().execute()
        if res.data:
            return res.data
    except Exception:
        pass
    return _LOCAL_STRATEGIES.get(strategy_id, {
        "id": strategy_id,
        "rank": 1,
        "total_score": 50.0,
        "sharpe_ratio": 1.0,
        "mc_robustness": 80.0,
        "strategy_tree": "gt(RSI, c_50)",
        "is_rl": False
    })

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
