from ...data.repositories.work_center import WorkCenterRepository
from ...data.models.work_center import WorkCenter
from ...api.v1.schemas.work_center import WorkCenterCreate, WorkCenterResponse
from ..exceptions.work_center_exception import WorkCenterNotFoundException


class WorkCenterService:
    def __init__(self, repository: WorkCenterRepository):
        self.repository = repository

    async def create(self, data: WorkCenterCreate) -> WorkCenterResponse:
        workcenter = WorkCenter(**data.model_dump())
        workcenter = await self.repository.create(workcenter)
        return WorkCenterResponse.model_validate(workcenter)

    async def get_all(self) -> list[WorkCenterResponse]:
        workcenters = await self.repository.get_all()
        return [WorkCenterResponse.model_validate(wc) for wc in workcenters]

    async def get_by_id(self, workcenter_id: int) -> WorkCenterResponse | None:
        workcenter = await self.repository.get_by_id(workcenter_id)
        if not workcenter:
            raise WorkCenterNotFoundException(workcenter_id)
        return WorkCenterResponse.model_validate(workcenter)
