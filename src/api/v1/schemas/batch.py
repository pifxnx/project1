from .product import ProductResponse
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)
from typing import Annotated, List, Literal
from datetime import datetime, date
from zoneinfo import ZoneInfo
from ....core.config import settings


PositiveInt32 = Annotated[int, Field(gt=0, le=2**31 - 1)]


class BatchModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @field_validator("shift_start", "shift_end", check_fields=False)
    @classmethod
    def ensure_aware(cls, value):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo(settings.production_timezone))
        return value

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
    batch_number: PositiveInt32 = Field(alias="НомерПартии")
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


class BatchCreateResponse(BatchModel):
    created: List[BatchResponse]
    errors: List[dict]


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
    batch_number: PositiveInt32 | None = None
    batch_date_from: date | None = None
    batch_date_to: date | None = None
    work_center_id: int | None = None
    shift: str | None = None


class BatchExportRequest(BaseModel):
    format: Literal["csv", "excel"]
    filters: BatchExportFilters

    model_config = ConfigDict(extra="forbid")


class AggregateRequest(BaseModel):
    unique_codes: List[str] = Field(min_length=1)


class BatchReportRequest(BaseModel):
    format: Literal["excel", "pdf"]
    email: EmailStr | None = None
