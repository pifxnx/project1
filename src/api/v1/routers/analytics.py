from fastapi import APIRouter, Depends, Body
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.batch import PositiveInt32
from ....core.cache import get_dashboard_statistics
from ....domain.services.analytics_service import AnalyticsService
from ....data.repositories.batch_repository import BatchRepository
from ....core.database import get_db


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_statistics():
    return await get_dashboard_statistics()


@router.post("/compare_batches")
async def compare_batches(
    session: Annotated[AsyncSession, Depends(get_db)],
    batch_ids: list[PositiveInt32] = Body(..., embed=True),
):
    repository = BatchRepository(session)
    service = AnalyticsService(repository)
    return await service.compare_batches(batch_ids)
