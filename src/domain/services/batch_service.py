from datetime import date
from typing import List
from ...data.repositories.batch_repository import BatchRepository
from ...api.v1.schemas.batch import BatchCreate, BatchResponse
from ...data.models.batch import Batch


class BatchService:
    def __init__(self, repository: BatchRepository):
        self.repository = repository

    async def create(self, data: BatchCreate) -> BatchResponse:
        batch = Batch(**data.model_dump())
        batch = await self.repository.create(batch)
        return BatchResponse(
            id=batch.id,
            is_closed=batch.is_closed,
            batch_number=batch.batch_number,
            batch_date=batch.batch_date,
            products=[]
        )

    async def get_by_id(self, batch_id: int) -> BatchResponse:
        batch = await self.repository.get_by_id(batch_id)

        ### написать исключение если не найдено

        return BatchResponse.model_validate(batch)

    async def get_batches(
            self,
            is_closed: bool | None = None,
            batch_number: int | None = None,
            batch_date: date | None = None, 
            work_center_id: int | None = None,
            shift: str | None = None, 
            offset: int = 0,
            limit: int = 20
    ) -> List[BatchResponse]:
        batches = await self.repository.get_with_filter(
            is_closed=is_closed,
            batch_number=batch_number,
            batch_date=batch_date,
            work_center_id=work_center_id,
            shift=shift,
            offset=offset,
            limit=limit
        )

        return [BatchResponse.model_validate(batch) for batch in batches]