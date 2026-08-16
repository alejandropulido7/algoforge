from fastapi import APIRouter, Depends
from algoforge.api.deps import get_current_user
from algoforge.services.export_service import export_strategy

router = APIRouter()

@router.get("/{strategy_id}/mt5")
def export_mt5(strategy_id: str, user: dict = Depends(get_current_user)):
    return {"code": export_strategy(strategy_id, "mt5")}

@router.get("/{strategy_id}/pine")
def export_pine(strategy_id: str, user: dict = Depends(get_current_user)):
    return {"code": export_strategy(strategy_id, "pine")}
