from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from algoforge.api.deps import get_current_user
from algoforge.schemas.data import DataSourceConfig
from algoforge.services.data_service import data_service

router = APIRouter()

@router.post("/fetch")
def fetch_data(config: DataSourceConfig, user: dict = Depends(get_current_user)):
    """Fetch OHLCV market data from provider or local dataset and return records."""
    df = data_service.fetch_ohlcv(
        symbol=config.symbol,
        timeframe=config.timeframe,
        start=config.start_date,
        end=config.end_date,
        source=config.source
    )
    # Format for charting / preview
    records = df.to_dict(orient="records")
    return {
        "success": True,
        "symbol": config.symbol,
        "timeframe": config.timeframe,
        "row_count": len(df),
        "data": records[:500]  # Return up to 500 bars for instant preview
    }

@router.post("/upload")
async def upload_data(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    """Upload custom CSV (including MT5 format) and index it as a selectable dataset."""
    contents = await file.read()
    result = data_service.upload_csv(contents, user["id"], file.filename)
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to parse CSV"))
    return result

@router.get("/datasets")
def list_datasets(user: dict = Depends(get_current_user)):
    """List all available datasets (uploaded MT5 CSVs + cached provider datasets)."""
    return {"datasets": data_service.list_datasets()}

@router.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: str, user: dict = Depends(get_current_user)):
    """Delete a custom dataset from storage."""
    success = data_service.delete_dataset(dataset_id)
    return {"success": success, "dataset_id": dataset_id}

@router.get("/symbols")
def get_symbols(user: dict = Depends(get_current_user)):
    """Return default supported market symbols."""
    return {"symbols": data_service.list_symbols()}
