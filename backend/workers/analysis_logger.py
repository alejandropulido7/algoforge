import os
from datetime import datetime

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")

def _ensure_logs_dir() -> str:
    os.makedirs(LOGS_DIR, exist_ok=True)
    return LOGS_DIR

class AnalysisLogger:
    """Per-analysis text logger. Writes a full trace of a job run to
    backend/logs/<job_id>.txt so every analysis has its own readable file."""

    def __init__(self, job_id: str):
        self.job_id = job_id
        _ensure_logs_dir()
        self.path = os.path.join(LOGS_DIR, f"{job_id}.txt")
        self._lines: list[str] = []
        self._write("=" * 78)
        self._write(f"AlgoForge Analysis Log - Job {job_id}")
        self._write(f"Started: {datetime.now().isoformat(timespec='seconds')}")
        self._write("=" * 78)

    def _write(self, line: str):
        self._lines.append(line)
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception as exc:
            print(f"[AnalysisLogger write error]: {exc}")

    def section(self, title: str):
        self._write("")
        self._write("-" * 78)
        self._write(f"[{datetime.now().strftime('%H:%M:%S')}] {title}")
        self._write("-" * 78)

    def info(self, message: str):
        self._write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def config(self, key: str, value):
        self._write(f"  {key}: {value}")

    def params(self, title: str, params: dict):
        self._write(f"  {title}:")
        if not params:
            self._write("    (sin parámetros / defaults de la librería)")
            return
        for k, v in params.items():
            self._write(f"    {k} = {v}")

    def close(self, status: str = "completed"):
        self._write("")
        self._write("=" * 78)
        self._write(f"Finished: {datetime.now().isoformat(timespec='seconds')} | Status: {status}")
        self._write("=" * 78)

    @property
    def lines(self) -> list[str]:
        return self._lines