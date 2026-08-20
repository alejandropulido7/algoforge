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
    
    if "tpslModes" not in config or config["tpslModes"] is None:
        config["tpslModes"] = [
            "atr_classic", "trailing_stop", "swing_structure", "time_exit",
            "percentage", "partial_tp", "breakeven", "fixed_pips", "smoothed_atr"
        ]

    if "tpslRanges" not in config or config["tpslRanges"] is None:
        config["tpslRanges"] = {}
    
    if "risk" not in config or not config["risk"]:
        config["risk"] = {
            "direction": "both",
            "orderType": "market",
            "maxSimultaneousTrades": 1,
            "consecutiveLossAction": "none",
            "consecutiveLossThreshold": 3,
            "consecutiveLossReductionPct": 50.0,
            "consecutiveLossReactivation": "none",
            "consecutiveLossCooldownBars": 20,
            "consecutiveLossCooldownDays": 1,
            "consecutiveLossAutoCooldown": True,
            "contractSize": 100000.0,
            "pointSize": 0.0001,
            "spreadPips": 1.0,
            "commissionPerLot": 7.0,
            "commissionPerSide": True,
            "swapPerLotPerDay": 0.0,
            "initialDeposit": 10000.0,
            "lotSize": 0.1,
            "slType": "none",
            "tpType": "none",
        }

    if "genetic" not in config or not config["genetic"]:
        config["genetic"] = {
            "populationSize": 100,
            "generations": 50,
            "crossoverProb": 0.7,
            "mutationProb": 0.1,
            "topStrategiesCount": 20
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
            target=run_strategy_pipeline.run,
            args=(job_id, config),
            kwargs={"user_id": user_id},
            daemon=True
        )
        t.start()

def get_job_status(job_id: str) -> dict:
    job = dict(_LOCAL_JOBS.get(job_id, {
        "id": job_id,
        "status": "running",
        "progress": 0,
        "current_phase": "queued",
        "config": {}
    }))
    client = get_supabase_client()
    try:
        res = client.table("jobs").select("*").eq("id", job_id).single().execute()
        if res.data:
            job.update(res.data)
    except Exception:
        pass

    # Check live Redis progress & metadata
    try:
        import redis, json
        from algoforge.config import settings
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        live_prog_str = r.get(f"job_combos:{job_id}:progress")
        if live_prog_str:
            live_prog = json.loads(live_prog_str)
            job["sub_current"] = live_prog.get("current", 0)
            job["sub_total"] = live_prog.get("total", 0)
            job["sub_progress"] = live_prog.get("sub_progress", 0)
            job["valid_candidates"] = live_prog.get("candidates", 0)
            if live_prog.get("message"):
                job["live_message"] = live_prog.get("message")
    except Exception:
        pass

    return job

def list_user_jobs(user_id: str) -> list[dict]:
    client = get_supabase_client()
    try:
        res = client.table("jobs").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        if res.data:
            return res.data
    except Exception:
        pass
    return [j for j in _LOCAL_JOBS.values() if j.get("user_id") == user_id]

def cancel_user_job(job_id: str, user_id: str, user_token: str | None = None) -> dict:
    """Cancel a running job by setting cancellation flag in Redis, Supabase, and Celery."""
    # 1. Set cancel flag in Redis with 1 hour expiration
    try:
        import redis
        from algoforge.config import settings
        r = redis.from_url(settings.REDIS_URL)
        r.set(f"cancel_job:{job_id}", "1", ex=3600)
    except Exception as e:
        print(f"[Redis cancel notice]: {e}")

    # 2. Try cancel/revoke running Celery task immediately
    try:
        from workers.celery_app import celery_app
        celery_app.control.revoke(job_id, terminate=True)
    except Exception as e:
        print(f"[Celery revoke notice]: {e}")

    # 3. Update local in-memory store
    if job_id in _LOCAL_JOBS:
        _LOCAL_JOBS[job_id]["status"] = "cancelled"
        _LOCAL_JOBS[job_id]["current_phase"] = "cancelled"
        _LOCAL_JOBS[job_id]["updated_at"] = datetime.now().isoformat()

    # 4. Update Supabase jobs table
    updated_db = False
    if user_token and user_token != "dev_mock_token":
        try:
            u_client = get_user_client(user_token)
            res = u_client.table("jobs").update({
                "status": "cancelled",
                "current_phase": "cancelled"
            }).eq("id", job_id).eq("user_id", user_id).execute()
            if res.data:
                updated_db = True
        except Exception as e:
            print(f"[Supabase user token cancel notice]: {e}")

    if not updated_db:
        try:
            client = get_supabase_client()
            client.table("jobs").update({
                "status": "cancelled",
                "current_phase": "cancelled"
            }).eq("id", job_id).execute()
        except Exception as e:
            print(f"[Supabase service cancel notice]: {e}")

    return {"status": "cancelled", "job_id": job_id}

def delete_user_job(job_id: str, user_id: str, user_token: str | None = None) -> dict:
    """Delete a job and its associated strategies from Supabase and local cache."""
    # 1. Try cancel/revoke running Celery task
    try:
        from workers.celery_app import celery_app
        celery_app.control.revoke(job_id, terminate=True)
    except Exception as e:
        print(f"[Celery revoke notice]: {e}")

    # 2. Purge from local memory
    _LOCAL_JOBS.pop(job_id, None)
    try:
        from algoforge.services.export_service import purge_local_strategies_by_job
        purge_local_strategies_by_job(job_id)
    except Exception as e:
        print(f"[Purge local strategies notice]: {e}")

    # 3. Delete from Supabase (strategies first, then job)
    deleted_from_db = False
    
    # Authenticated user client
    if user_token and user_token != "dev_mock_token":
        try:
            u_client = get_user_client(user_token)
            # Delete child strategies
            u_client.table("strategies").delete().eq("job_id", job_id).execute()
            # Delete job
            res = u_client.table("jobs").delete().eq("id", job_id).eq("user_id", user_id).execute()
            if res.data:
                deleted_from_db = True
        except Exception as e:
            print(f"[Supabase user token delete notice]: {e}")

    # Fallback to service role client
    if not deleted_from_db:
        try:
            client = get_supabase_client()
            client.table("strategies").delete().eq("job_id", job_id).execute()
            client.table("jobs").delete().eq("id", job_id).execute()
        except Exception as e:
            print(f"[Supabase service delete fallback notice]: {e}")

    return {"status": "deleted", "job_id": job_id}
