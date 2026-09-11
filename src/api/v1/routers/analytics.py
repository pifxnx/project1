from fastapi import APIRouter
from ....core.cache import get_dashboard_statistics


router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_statistics():
    return await get_dashboard_statistics()
