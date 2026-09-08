from pydantic import BaseModel, ConfigDict
from datetime import datetime

class WorkCenterModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class WorkCenterCreate(WorkCenterModel):
    identifier: str 
    name: str


class WorkCenterResponse(WorkCenterModel):
    id: int
    identifier: str
    name: str 
    created_at: datetime
    updated_at: datetime