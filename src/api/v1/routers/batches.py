from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from datetime import date
from ....core.database import get_db
from ..schemas.batch import BatchCreate, BatchResponse, BatchWithProductsResponse
from ....domain.services.batch_service import BatchService
from ....data.repositories.batch_repository import BatchRepository
from ....tasks.aggregation import aggregate_products_batch_task
from ....core.cache import get_batch_with_products, get_batches_list

router = APIRouter(prefix="/batches", tags=["batches"])

@router.get("/{batch_id}", response_model=BatchWithProductsResponse)
async def get_batch(batch_id: int):
    return await get_batch_with_products(batch_id)


@router.post("/", response_model=BatchResponse)
async def create_batch(
    data: BatchCreate,
    session: AsyncSession = Depends(get_db)
):
    repository = BatchRepository(session)
    service = BatchService(repository)

    return await service.create(data)


@router.get("/", response_model=List[BatchResponse])
async def get_batches(
    session: Annotated[AsyncSession, Depends(get_db)],
    is_closed: bool | None = None,
    batch_number: int | None = None,
    batch_date: date | None = None,
    work_center_id: int | None = None, 
    shift: str | None = None,
    offset: int = Query(0, ge=0), 
    limit: int = Query(20, le=100),
):
    if (batch_number is None and batch_date is None
        and work_center_id is None and shift is None):
        return await get_batches_list(
            is_closed=is_closed,
            offset=offset,
            limit=limit
        )
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

@router.patch("/{batch_id}", response_model=BatchResponse)
async def set_is_closed(
    session: Annotated[AsyncSession, Depends(get_db)], 
    batch_id: int
) -> BatchResponse:
    repository = BatchRepository(session)
    service = BatchService(repository)

    return await service.set_is_closed(batch_id)


@router.post("/{batch_id}/aggregate")
async def aggregate(
    batch_id: int,
    unique_codes: list[str]
) -> dict:
   result = aggregate_products_batch_task.delay(batch_id, unique_codes)

   return {
       "task_id": result.id,
       "status": result.status,
       "message": "Aggregation task started"
   }