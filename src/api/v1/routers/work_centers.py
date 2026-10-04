from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from ....core.database import get_db
from ..schemas.work_center import WorkCenterCreate, WorkCenterResponse
from ....data.repositories.work_center import WorkCenterRepository
from ....domain.services.work_center_service import WorkCenterService

router = APIRouter(prefix="/work_center", tags=["work_center"])


@router.post(
    "/", response_model=WorkCenterResponse, status_code=status.HTTP_201_CREATED
)
async def create_work_center(
    session: Annotated[AsyncSession, Depends(get_db)], workcenter: WorkCenterCreate
):
    repository = WorkCenterRepository(session)
    service = WorkCenterService(repository)

    return await service.create(workcenter)


@router.get("/work_centers", response_model=list[WorkCenterResponse])
async def get_work_centers(session: Annotated[AsyncSession, Depends(get_db)]):
    repository = WorkCenterRepository(session)
    service = WorkCenterService(repository)

    return await service.get_all()
