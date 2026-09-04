from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import date
from typing import List
from datetime import datetime, timezone
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
        stmt = select(Batch).options(selectinload(Batch.products)).where(Batch.id == batch_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_filter(
            self,
            is_closed: bool | None = None,
            batch_number: int | None = None,
            batch_date: date | None = None, 
            work_center_id: int | None = None,
            shift: str | None = None, 
            offset: int = 0,
            limit: int = 20
    ) -> List[Batch]:
        stmt = select(Batch).options(selectinload(Batch.products))
        if is_closed is not None:
            stmt = stmt.where(Batch.is_closed == is_closed)
        if batch_number is not None:
            stmt = stmt.where(Batch.batch_number == batch_number)
        if batch_date is not None:
            stmt = stmt.where(Batch.batch_date == batch_date)
        if work_center_id is not None:
            stmt = stmt.where(Batch.work_center_id == work_center_id)
        if shift is not None:
            stmt = stmt.where(Batch.shift == shift)

        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())


    async def set_is_closed(self, id: int) -> Batch | None:
        batch = await self.session.get(Batch, id)
        if not batch:
            return None ### дописать исключение

        if not batch.is_closed:
            batch.is_closed = True
            batch.closed_at = datetime.now(timezone.utc)

        else: 
            batch.is_closed = False
            batch.closed_at = None

        await self.session.commit()

        return batch