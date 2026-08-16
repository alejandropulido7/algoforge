from typing import Optional
from pydantic import BaseModel, Field

class DataSourceConfig(BaseModel):
    symbol: str = "BTC-USD"
    timeframe: str = "1d"
    start_date: Optional[str] = Field(default=None, alias="startDate")
    end_date: Optional[str] = Field(default=None, alias="endDate")
    source: str = "yfinance"
    upload_file_id: Optional[str] = None

    class Config:
        populate_by_name = True

class DatasetInfo(BaseModel):
    id: str
    symbol: str
    name: str
    timeframe: str
    start_date: str
    end_date: str
    row_count: int
    source: str
    created_at: str
