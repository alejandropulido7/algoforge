import uuid
import threading
from datetime import datetime
from algoforge.supabase.client import get_supabase_client, get_user_client
from workers.tasks import run_strategy_pipeline

# Local in-memory store for instant lookup & offline fallback
_LOCAL_JOBS: dict[str, dict] = {}

def _normalize_config(raw: dict) -> dict:
    """Normalize flat or nested job config dictionary."""
    config = dict(raw)
    
    # If dataSource is missing but flat symbol/timeframe exist
    if "dataSource" not in config or not config["dataSource"]:
        config["dataSource"] = {
            "source": config.get("data_source", "yfinance"),
            "symbol": config.get("symbol", "BTC-USD"),
            "timeframe": config.get("timeframe", "1d"),
            "startDate": config.get("start_date", "2023-01-01"),
            "endDate": config.get("end_date", "2024-01-01")
        }
    
    if "indicators" not in config or config["indicators"] is None:
        config["indicators"] = ["RSI", "SMA"]
    
    if "risk" not in config or not config["risk"]:
        config["risk"] = {
            "initialDeposit": 10000.0,
            "sizingMode": "lots",
            "lotSize": 0.1,
            "riskPct": 1.0,
            "slType": "pips",
            "slPips": 50.0,
            "slAtrMult": 1.5,
            "tpType": "pips",
            "tpPips": 100.0,
            "tpAtrMult": 3.0,
            "contractSize": 100000.0,
            "pointSize": 0.0001,
            "commissionPerLot": 7.0
        }

    if "genetic" not in config or not config["genetic"]:
        config["genetic"] = {
            "populationSize": 100,
            "generations": 50,
            "crossoverProb": 0.7,
            "mutationProb": 0.1
        }
    
    if "rl" not in config or not config["rl"]:
        config["rl"] = {
            "enabled": False,
            "algorithm": "ppo",
            "timesteps": 100000,
            "learningRate": 0.0003
        }

    if "montecarlo" not in config or not config["montecarlo"]:
        config["montecarlo"] = {
            "simulations": 1000,
            "method": "permutation",
            "ruinThreshold": 20
        }

    return config

def create_job(user_id: str, raw_config: dict, user_token: str | None = None) -> dict:
    """Create a new job record and dispatch strategy pipeline with synchronized task_id."""
    config = _normalize_config(raw_config)
    job_id = str(uuid.uuid4())
    
    job_record = {
        "id": job_id,
        "user_id": user_id,
        "config": config,
        "status": "running",
        "progress": 0,
        "current_phase": "queued",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    _LOCAL_JOBS[job_id] = job_record

    # 1. Try insert with user's authenticated JWT client (respects RLS)
    saved_to_db = False
    if user_token and user_token != "dev_mock_token":
        try:
            u_client = get_user_client(user_token)
            res = u_client.table("jobs").insert({
                "id": job_id,
                "user_id": user_id,
                "config": config,
                "status": "running",
                "progress": 0,
                "current_phase": "queued"
            }).execute()
            if res.data:
                saved_to_db = True
                print(f"[Supabase authenticated insert success]: {job_id}")
        except Exception as e:
            print(f"[Supabase user token insert notice]: {e}")

    # 2. Try insert with service_role / system client
    if not saved_to_db:
        try:
            client = get_supabase_client()
            res = client.table("jobs").insert({
                "id": job_id,
                "user_id": user_id,
                "config": config,
                "status": "running",
                "progress": 0,
                "current_phase": "queued"
            }).execute()
            if res.data:
                saved_to_db = True
                print(f"[Supabase service client insert success]: {job_id}")
        except Exception as e:
            print(f"[Supabase service insert fallback]: {e}")

    # 3. Dispatch to Celery with task_id explicitly set to job_id!
    _dispatch_pipeline(job_id, config, user_id)

    return {
        "id": job_id,
        "job_id": job_id,
        "user_id": user_id,
        "status": "running",
        "progress": 0,
        "current_phase": "queued",
        "config": config,
        "created_at": job_record["created_at"]
    }

def _dispatch_pipeline(job_id: str, config: dict, user_id: str):
    """Try Celery queue using task_id=job_id; if Celery worker is offline, run in background thread."""
    try:
        res = run_strategy_pipeline.apply_async(
            args=[job_id, config],
            kwargs={"user_id": user_id},
            task_id=job_id
        )
        print(f"[Celery task queued with matching task_id]: {res.id}")
    except Exception as e:
        print(f"[Celery dispatch exception, running in thread fallback]: {e}")
        t = threading.Thread(
            target=run_strategy_pipeline,
            args=(None, job_id, config),
            kwargs={"user_id": user_id},
            daemon=True
        )
        t.start()

def get_job_status(job_id: str) -> dict:
    client = get_supabase_client()
    try:
        res = client.table("jobs").select("*").eq("id", job_id).single().execute()
        if res.data:
            return res.data
    except Exception:
        pass
    return _LOCAL_JOBS.get(job_id, {
        "id": job_id,
        "status": "running",
        "progress": 50,
        "current_phase": "genetic",
        "config": {}
    })

def list_user_jobs(user_id: str) -> list[dict]:
    client = get_supabase_client()
    try:
        res = client.table("jobs").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        if res.data:
            return res.data
    except Exception:
        pass
    return [j for j in _LOCAL_JOBS.values() if j.get("user_id") == user_id]
