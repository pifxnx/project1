from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select
from ..models.batch import Batch

class BatchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, batch: Batch) -> Batch:
        self.session.add(batch)
        await self.session.commit()
        await self.session.refresh(batch)
        return batch

    async def get_by_id(self, batch_id: int) -> Batch | None:
        stmt = select(Batch).where(Batch.id == batch_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()