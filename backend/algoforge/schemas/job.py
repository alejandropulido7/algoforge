from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

class DataSourceConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    source: str = "yfinance"
    symbol: str = "BTC-USD"
    timeframe: str = "1d"
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class RiskConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    initialDeposit: float = 10000.0
    sizingMode: str = "lots"  # "lots" | "risk_pct" | "cash"
    lotSize: float = 0.1
    riskPct: float = 1.0
    slType: str = "pips"      # "pips" | "atr" | "none"
    slPips: float = 50.0
    slAtrMult: float = 1.5
    tpType: str = "pips"      # "pips" | "atr" | "none"
    tpPips: float = 100.0
    tpAtrMult: float = 3.0
    contractSize: float = 100000.0
    pointSize: float = 0.0001
    commissionPerLot: float = 7.0

class GeneticConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    populationSize: int = 100
    generations: int = 50
    crossoverProb: float = 0.7
    mutationProb: float = 0.1

class RLConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    enabled: bool = False
    algorithm: str = "ppo"
    timesteps: int = 100000
    learningRate: float = 0.0003

class MonteCarloConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    simulations: int = 1000
    method: str = "permutation"
    ruinThreshold: int = 20

class JobCreate(BaseModel):
    model_config = ConfigDict(extra="allow")

    # Nested frontend structure
    dataSource: Optional[Dict[str, Any]] = None
    indicators: Optional[List[str]] = Field(default_factory=list)
    indicatorParams: Optional[Dict[str, Any]] = Field(default_factory=dict)
    risk: Optional[Dict[str, Any]] = None
    genetic: Optional[Dict[str, Any]] = None
    rl: Optional[Dict[str, Any]] = None
    montecarlo: Optional[Dict[str, Any]] = None

    # Flat / legacy fields
    symbol: Optional[str] = None
    timeframe: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    data_source: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class JobStatus(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    status: str
    progress: float
    current_phase: str
    error_message: Optional[str] = None

class JobResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    user_id: str
    status: str
    config: Dict[str, Any]
    progress: float
    current_phase: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None
