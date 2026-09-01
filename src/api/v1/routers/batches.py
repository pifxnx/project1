from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ....core.database import get_db
from ..schemas.batch import BatchCreate, BatchResponse
from ....domain.services.batch_service import BatchService
from ....data.repositories.batch import BatchRepository

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