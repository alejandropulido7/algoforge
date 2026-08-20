class ProgressCallback:
    """Updates job progress and status in the Supabase database."""

    def __init__(self, job_id: str, supabase_client):
        self.job_id = job_id
        self.client = supabase_client

    def update(self, progress: int, message: str = "", phase: str = "running", status: str | None = None):
        payload = {
            "progress": int(progress),
            "current_phase": phase,
        }
        if status:
            payload["status"] = status
        elif progress >= 100 and phase == "done":
            payload["status"] = "completed"
        elif progress > 0:
            payload["status"] = "running"

        if message:
            payload["error_message"] = message if "failed" in phase.lower() or (status and status == "failed") else None

        try:
            self.client.table("jobs").update(payload).eq("id", self.job_id).execute()
        except Exception:
            # Fallback when running without remote DB
            pass

        try:
            from algoforge.services.job_service import _LOCAL_JOBS
            if self.job_id in _LOCAL_JOBS:
                _LOCAL_JOBS[self.job_id]["progress"] = int(progress)
                _LOCAL_JOBS[self.job_id]["current_phase"] = phase
                if status:
                    _LOCAL_JOBS[self.job_id]["status"] = status
                elif progress >= 100 and phase == "done":
                    _LOCAL_JOBS[self.job_id]["status"] = "completed"
                elif progress > 0:
                    _LOCAL_JOBS[self.job_id]["status"] = "running"
                if message:
                    _LOCAL_JOBS[self.job_id]["live_message"] = message
        except Exception:
            pass

    def is_cancelled(self) -> bool:
        """Check if job cancellation has been requested via Redis."""
        try:
            import redis
            from algoforge.config import settings
            r = redis.from_url(settings.REDIS_URL)
            val = r.get(f"cancel_job:{self.job_id}")
            if val:
                return True
        except Exception:
            pass
        return False

