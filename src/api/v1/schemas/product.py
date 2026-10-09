from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


PositiveInt32 = Annotated[int, Field(gt=0, le=2**31 - 1)]


class ProductModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProductResponse(ProductModel):
    id: int
    unique_code: str
    is_aggregated: bool
    aggregated_at: datetime | None = None


class ProductCreate(ProductModel):
    unique_code: str
    batch_id: PositiveInt32
