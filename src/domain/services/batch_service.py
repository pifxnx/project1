from datetime import date
from typing import List
from ...data.repositories.batch_repository import BatchRepository
from ...api.v1.schemas.batch import BatchCreate, BatchResponse, BatchAlter
from ...data.models.batch import Batch
from ..exceptions.batch_exception import (
    BatchNotFoundException, BatchAlreadyExistsException
)
from ...tasks.webhooks import create_webhook_delivery


class BatchService:
    def __init__(self, repository: BatchRepository):
        self.repository = repository

    async def create(self, data: BatchCreate) -> BatchResponse:
        batch = Batch(**data.model_dump())
        existing = await self.repository.get_by_number_and_date(batch.batch_number, batch.batch_date)
        if existing:
            raise BatchAlreadyExistsException()

        batch = await self.repository.create(batch)

        create_webhook_delivery.delay(
            "batch_created",
            {"id": batch.id, "batch_number": batch.batch_number,
             "batch_date": batch.batch_date.isoformat(), "nomenclature": batch.nomenclature,
             "work_center": batch.work_center_id}
        )

        return BatchResponse(
            id=batch.id,
            is_closed=batch.is_closed,
            batch_number=batch.batch_number,
            batch_date=batch.batch_date,
            products=[]
        )

    async def get_by_id(self, batch_id: int) -> BatchResponse:
        batch = await self.repository.get_by_id(batch_id)

        if not batch:
            raise BatchNotFoundException(batch_id)

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

    async def update(self, id: int, data: BatchAlter) -> BatchResponse:
        batch = await self.repository.update(id, data)
        if not batch:
            raise BatchNotFoundException(id)

        create_webhook_delivery.delay(
            "batch_updated",
            {"id": batch.id, "batch_number": batch.batch_number,
             "changes": data.model_dump(exclude_unset=True)}
        )

        return BatchResponse.model_validate(batch)

    async def set_is_closed(self, id: int) -> BatchResponse:
        batch = await self.repository.set_is_closed(id)

        return BatchResponse.model_validate(batch)