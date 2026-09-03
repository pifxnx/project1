from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from datetime import date
from ....core.database import get_db
from ..schemas.batch import BatchCreate, BatchResponse
from ....domain.services.batch_service import BatchService
from ....data.repositories.batch_repository import BatchRepository

router = APIRouter(prefix="/batches", tags=["batches"])

@router.get("/{batch_id}", response_model=BatchResponse)
async def get_batch(
    batch_id: int,
    session: AsyncSession = Depends(get_db)
):
    repository = BatchRepository(session=session)
    service = BatchService(repository)

    return await service.get_by_id(batch_id)

@router.post("/", response_model=BatchResponse)
async def create_batch(
    data: BatchCreate,
    session: AsyncSession = Depends(get_db)
):
    repository = BatchRepository(session)
    service = BatchService(repository)

    return await service.create(data)


@router.get("/", response_model=List[BatchResponse])
async def get_batches_filter(
    is_closed: bool | None,
    batch_number: int | None,
    batch_date: date | None,
    work_center_id: int | None, 
    shift: str | None,
    session: Annotated[AsyncSession, Depends(get_db)],
    offset: int = Query(0, ge=0), 
    limit: int = Query(20, le=100),
) -> List[BatchResponse]:
    repository = BatchRepository(session)
    service = BatchService(repository)

    return await service.get_batches(
        is_closed=is_closed,
        batch_number=batch_number,
        batch_date=batch_date,
        work_center_id=work_center_id,
        shift=shift,
        offset=offset,
        limit=limit,
    )