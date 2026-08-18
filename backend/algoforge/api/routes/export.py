import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from algoforge.api.deps import get_current_user
from algoforge.services.export_service import export_strategy, get_onnx_filepath

router = APIRouter()

@router.get("/indicators")
def export_indicators_zip(user: dict = Depends(get_current_user)):
    from algoforge.services.export_service import export_all_indicators
    zip_buffer = export_all_indicators()
    if not zip_buffer:
        raise HTTPException(status_code=500, detail="Failed to generate indicators ZIP")
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=AlgoForge_MT5_Indicators.zip"}
    )

@router.get("/{strategy_id}/mt5")
def export_mt5(strategy_id: str, user: dict = Depends(get_current_user)):
    return {"code": export_strategy(strategy_id, "mt5")}

@router.get("/{strategy_id}/pine")
def export_pine(strategy_id: str, user: dict = Depends(get_current_user)):
    return {"code": export_strategy(strategy_id, "pine")}

@router.get("/{strategy_id}/python")
def export_python(strategy_id: str, user: dict = Depends(get_current_user)):
    return {"code": export_strategy(strategy_id, "python")}

@router.get("/{strategy_id}/onnx")
def download_onnx(strategy_id: str, user: dict = Depends(get_current_user)):
    file_path = get_onnx_filepath(strategy_id)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="ONNX model file not found for this strategy.")
    filename = os.path.basename(file_path)
    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=filename
    )
