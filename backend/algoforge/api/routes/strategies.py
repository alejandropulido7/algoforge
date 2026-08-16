from fastapi import APIRouter, Depends
from algoforge.api.deps import get_supabase

router = APIRouter()

@router.get("")
def list_strategies(job_id: str, db = Depends(get_supabase)):
    res = db.table("strategies").select("*").eq("job_id", job_id).execute()
    return res.data

@router.get("/{strategy_id}")
def get_strategy(strategy_id: str, db = Depends(get_supabase)):
    res = db.table("strategies").select("*").eq("id", strategy_id).single().execute()
    return res.data
