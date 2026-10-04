from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import date
from typing import List
from datetime import datetime, timezone
from ..models.batch import Batch
from ..models.work_center import WorkCenter
from ...api.v1.schemas.batch import BatchAlter


class BatchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_work_center(
        self, identifier: str, name: str
    ) -> WorkCenter:
        stmt = select(WorkCenter).where(WorkCenter.identifier == identifier)
        result = await self.session.execute(stmt)
        work_center = result.scalar_one_or_none()

        if not work_center:
            work_center = WorkCenter(identifier=identifier, name=name)
            self.session.add(work_center)
            await self.session.commit()
            await self.session.refresh(work_center)

        return work_center

    async def create(self, batch: Batch) -> Batch:
        self.session.add(batch)
        await self.session.commit()
        await self.session.refresh(batch)
        return batch

    async def get_by_id(self, batch_id: int) -> Batch | None:
        stmt = (
            select(Batch)
            .options(selectinload(Batch.products))
            .where(Batch.id == batch_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, batch_ids: list[int]) -> List[Batch]:
        stmt = (
            select(Batch)
            .options(selectinload(Batch.products))
            .where(Batch.id.in_(batch_ids))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_number_and_date(
        self, batch_number: int, batch_date: date
    ) -> Batch | None:
        stmt = select(Batch).where(
            Batch.batch_number == batch_number, Batch.batch_date == batch_date
        )
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
        limit: int = 20,
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

    async def update(self, id: int, data: BatchAlter) -> tuple[Batch | None, bool]:
        batch = await self.session.get(Batch, id)
        closed_now = False
        if batch:
            before = batch.is_closed
            changes = data.model_dump(exclude_unset=True)
            if changes.get("is_closed", True) is None:
                changes.pop("is_closed")
            if "is_closed" in changes and changes["is_closed"] != batch.is_closed:
                batch.closed_at = (
                    datetime.now(timezone.utc) if changes["is_closed"] else None
                )

            for field, value in changes.items():
                setattr(batch, field, value)

            await self.session.commit()
            await self.session.refresh(batch)
            closed_now = not before and batch.is_closed

        return batch, closed_now
