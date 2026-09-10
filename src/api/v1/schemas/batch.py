from .product import ProductResponse
from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime, date

class BatchModel(BaseModel):
    model_config = ConfigDict(from_attributes=True) 

class BatchCreate(BatchModel):
    is_closed: bool 
    task_description: str 
    work_center_id: int
    shift: str
    team: str 
    ekn_code: str
    batch_number: int 
    batch_date: date
    nomenclature: str
    shift_start: datetime
    shift_end: datetime

class BatchResponse(BatchModel):
    id: int
    is_closed: bool
    batch_number: int 
    batch_date: date 
    products: List[ProductResponse]


class BatchAlter(BatchModel):
    is_closed: bool | None = None
    task_description: bool | None = None
    shift: str | None = None
    team: str | None = None
    ekn_code: str | None = None
    nomenclature: str | None = None
    shift_start: datetime | None = None
    shift_end: datetime | None = None

