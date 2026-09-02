from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ProductModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProductResponse(ProductModel):
    id: int
    unique_code: str 
    is_aggregated: bool 
    aggregated_at: datetime | None = None


class ProductCreate(ProductModel):
    unique_code: str 
    batch_id: int