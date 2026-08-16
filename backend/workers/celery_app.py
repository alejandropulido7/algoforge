import os

# macOS Fork safety and single-threading to prevent SIGABRT with PyTorch / OpenMP in Celery
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

try:
    import torch
    torch.set_num_threads(1)
except Exception:
    pass

from celery import Celery
from algoforge.config import settings

celery_app = Celery(
    "algoforge_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.REDIS_URL,
    include=["workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_pool_restarts=True,
)

# Explicitly import tasks so the registry is populated immediately upon importing celery_app
try:
    import workers.tasks  # noqa: E402, F401
except ImportError:
    pass
