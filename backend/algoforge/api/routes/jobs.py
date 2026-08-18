from fastapi import APIRouter, Depends
from algoforge.api.deps import get_current_user
from algoforge.schemas.job import JobCreate
from algoforge.services.job_service import create_job, get_job_status, list_user_jobs, delete_user_job

router = APIRouter()

@router.post("")
def create_new_job(job: JobCreate, user: dict = Depends(get_current_user)):
    return create_job(user["id"], job.model_dump(), user_token=user.get("token"))

@router.get("")
def list_jobs(user: dict = Depends(get_current_user)):
    return list_user_jobs(user["id"])

@router.get("/{job_id}")
def get_status(job_id: str, user: dict = Depends(get_current_user)):
    return get_job_status(job_id)

@router.delete("/{job_id}")
def delete_job(job_id: str, user: dict = Depends(get_current_user)):
    return delete_user_job(job_id, user["id"], user_token=user.get("token"))
