from fastapi import APIRouter
from celery.result import AsyncResult


router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/{task_id}")
async def get_task_by_id(task_id: str) -> dict:
    result = AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result
    }