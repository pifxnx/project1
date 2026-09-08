from sqlalchemy.ext.asyncio import AsyncSession
from ..models.work_center import WorkCenter


class WorkCenterRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def create(self, workcenter: WorkCenter) -> WorkCenter:
        self.session.add(workcenter)
        await self.session.commit()
        await self.session.refresh(workcenter)

        return workcenter

