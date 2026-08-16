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
