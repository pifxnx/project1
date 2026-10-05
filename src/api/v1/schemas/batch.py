from .product import ProductResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Literal
from datetime import datetime, date


class BatchModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def check_shift_range(self):
        start = getattr(self, "shift_start", None)
        end = getattr(self, "shift_end", None)
        if start is not None and end is not None and end <= start:
            raise ValueError("shift_end must be greater than shift_start")
        return self


class BatchCreateRu(BatchModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    is_closed: bool = Field(False, alias="СтатусЗакрытия")
    task_description: str = Field(alias="ПредставлениеЗаданияНаСмену")
    work_center_name: str = Field(alias="РабочийЦентр")
    work_center_identifier: str = Field(alias="ИдентификаторРЦ")
    shift: str = Field(alias="Смена")
    team: str = Field(alias="Бригада")
    ekn_code: str = Field(alias="КодЕКН")
    batch_number: int = Field(alias="НомерПартии")
    batch_date: date = Field(alias="ДатаПартии")
    nomenclature: str = Field(alias="Номенклатура")
    shift_start: datetime = Field(alias="ДатаВремяНачалаСмены")
    shift_end: datetime = Field(alias="ДатаВремяОкончанияСмены")


class BatchCreate(BatchModel):
    is_closed: bool = False
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


class BatchWithProductsResponse(BatchModel):
    id: int
    is_closed: bool
    batch_number: int
    batch_date: date
    products: List[ProductResponse]


class BatchAlter(BatchModel):
    is_closed: bool | None = None
    task_description: str | None = None
    shift: str | None = None
    team: str | None = None
    ekn_code: str | None = None
    nomenclature: str | None = None
    shift_start: datetime | None = None
    shift_end: datetime | None = None


class BatchExportFilters(BaseModel):
    is_closed: bool | None = None
    batch_number: int | None = None
    batch_date_from: date | None = None
    batch_date_to: date | None = None
    work_center_id: int | None = None
    shift: str | None = None


class BatchExportRequest(BaseModel):
    format: Literal["csv", "excel"]
    filters: BatchExportFilters

    model_config = ConfigDict(extra="forbid")
