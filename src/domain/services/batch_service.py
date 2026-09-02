from ...data.repositories.batch_repository import BatchRepository
from ...api.v1.schemas.batch import BatchCreate, BatchResponse
from ...data.models.batch import Batch


class BatchService:
    def __init__(self, repository: BatchRepository):
        self.repository = repository

    async def create(self, data: BatchCreate) -> BatchResponse:
        batch = Batch(**data.model_dump())
        batch = await self.repository.create(batch)
        return BatchResponse.model_validate(batch)

    async def get_by_id(self, batch_id: int) -> BatchResponse:
        batch = await self.repository.get_by_id(batch_id)

        ### написать исключение если не найдено

        return BatchResponse.model_validate(batch)