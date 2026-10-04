from fastapi import APIRouter, Depends, Query, UploadFile, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from datetime import date
from ....core.database import get_db
from ..schemas.batch import (
    BatchCreateRu,
    BatchResponse,
    BatchAlter,
    BatchWithProductsResponse,
    BatchExportFilters,
    BatchExportRequest,
)
from ....domain.services.batch_service import BatchService, ImportExportService
from ....data.repositories.batch_repository import BatchRepository
from ....data.repositories.product_repository import ProductRepository
from ....domain.services.product_service import ProductService, AggregationService
from ....tasks.aggregation import aggregate_products_task
from ....core.cache import get_batch_with_products, get_batches_list
from ....domain.services.analytics_service import AnalyticsService
from ....tasks.reports import generate_batch_report
from ....domain.exceptions.batch_exception import BatchNotFoundException

router = APIRouter(prefix="/batches", tags=["batches"])


@router.get("/{batch_id}", response_model=BatchWithProductsResponse)
async def get_batch(batch_id: int):
    batch = await get_batch_with_products(batch_id)
    if batch is None:
        raise BatchNotFoundException(batch_id)

    return batch


@router.post(
    "/", response_model=List[BatchResponse], status_code=status.HTTP_201_CREATED
)
async def create_batches(
    data: List[BatchCreateRu], session: AsyncSession = Depends(get_db)
):
    repository = BatchRepository(session)
    service = BatchService(repository)

    return await service.create_many(data)


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
    if (
        batch_number is None
        and batch_date is None
        and work_center_id is None
        and shift is None
    ):
        return await get_batches_list(is_closed=is_closed, offset=offset, limit=limit)
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
async def update_batch(
    session: Annotated[AsyncSession, Depends(get_db)], batch_id: int, data: BatchAlter
):
    repository = BatchRepository(session)
    service = BatchService(repository)

    return await service.update(batch_id, data)


@router.post("/{batch_id}/aggregate", status_code=status.HTTP_200_OK)
async def aggregate(
    session: Annotated[AsyncSession, Depends(get_db)],
    batch_id: int,
    unique_codes: list[str],
) -> dict:
    service = AggregationService(ProductRepository(session))

    return await service.aggregate_products_batch(batch_id, unique_codes)


@router.post("/{batch_id}/aggregate-async", status_code=status.HTTP_202_ACCEPTED)
async def aggregate_async(batch_id: int, unique_codes: list[str]) -> dict:
    service = AggregationService()

    return await service.aggregate_products_batch_async(batch_id, unique_codes)


@router.get("/{batch_id}/statistics")
async def get_batch_statistics(
    session: Annotated[AsyncSession, Depends(get_db)], batch_id: int
) -> dict:
    repository = BatchRepository(session)
    service = AnalyticsService(repository)

    return await service.get_batch_statistics(batch_id)


@router.post("/{batch_id}/reports", status_code=status.HTTP_202_ACCEPTED)
async def create_report(
    session: Annotated[AsyncSession, Depends(get_db)], batch_id
) -> dict:
    repository = BatchRepository(session)
    service = BatchService(repository)

    return await service.create_batch_report(batch_id)


@router.post("/import", status_code=status.HTTP_202_ACCEPTED)
async def upload_file(file: UploadFile):
    content = await file.read()

    if not file.filename:
        return

    service = ImportExportService()
    return await service.import_batch(content, file.filename)


@router.post("/export", status_code=status.HTTP_202_ACCEPTED)
async def export_batches(data: BatchExportRequest):
    service = ImportExportService()

    return await service.export_batches(data.model_dump(mode="json", exclude_none=True))
