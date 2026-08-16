from engine.exporters.mt5_exporter import MT5Exporter
from engine.exporters.pine_exporter import PineScriptExporter
from algoforge.supabase.client import get_supabase_client

def export_strategy(strategy_id: str, format: str):
    client = get_supabase_client()
    strategy = client.table("strategies").select("*").eq("id", strategy_id).single().execute().data
    
    if format == "mt5":
        return MT5Exporter().export(strategy)
    elif format == "pine":
        return PineScriptExporter().export(strategy)
    return ""
