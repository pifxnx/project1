from ...data.repositories.work_center import WorkCenterRepository
from ...data.models.work_center import WorkCenter 
from ...api.v1.schemas.work_center import (
    WorkCenterCreate,
    WorkCenterResponse
)


class WorkCenterService:
    def __init__(self, repository: WorkCenterRepository):
        self.repository = repository

    async def create(self, data: WorkCenterCreate) -> WorkCenterResponse:
        workcenter = WorkCenter(**data.model_dump())
        workcenter = await self.repository.create(workcenter)
        return WorkCenterResponse.model_validate(workcenter)