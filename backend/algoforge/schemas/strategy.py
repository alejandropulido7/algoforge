from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class StrategyScore(BaseModel):
    sharpe: float
    mc_robustness: float
    return_pct: float
    drawdown_pct: float
    win_rate: float
    profit_factor: float
    total_score: float

class StrategyResponse(BaseModel):
    id: str
    job_id: str
    rank: int
    scores: StrategyScore
    created_at: datetime

class StrategyDetail(StrategyResponse):
    indicators: List[Dict[str, Any]]
    rules: Dict[str, Any]
    equity_curve: List[float]
    trade_log: List[Dict[str, Any]]
