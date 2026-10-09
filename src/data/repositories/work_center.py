from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..models.work_center import WorkCenter


class WorkCenterRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, workcenter: WorkCenter) -> WorkCenter:
        self.session.add(workcenter)
        await self.session.commit()
        await self.session.refresh(workcenter)

        return workcenter

    async def get_all(self) -> List[WorkCenter]:
        stmt = select(WorkCenter)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, workcenter_id: int) -> WorkCenter | None:
        stmt = select(WorkCenter).where(WorkCenter.id == workcenter_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
