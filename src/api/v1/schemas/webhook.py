from pydantic import BaseModel, ConfigDict, HttpUrl
from datetime import datetime
from typing import List, Literal


event_type = Literal[
    "batch_created",
    "batch_updated",
    "batch_closed",
    "product_aggregated",
    "report_generated",
    "import_completed",
]


class WebhookSubscriptionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class WebhookSubscriptionCreate(WebhookSubscriptionModel):
    url: HttpUrl
    events: List[event_type]
    # secret_key: str
    retry_count: int | None = 3
    timeout: int | None = 10


class WebhookSubscriptionCreateResponse(WebhookSubscriptionModel):
    id: int
    url: HttpUrl
    events: List[event_type]
    secret_key: str
    is_active: bool
    retry_count: int
    timeout: int
    created_at: datetime
    updated_at: datetime


class WebhookSubscriptionResponse(WebhookSubscriptionModel):
    id: int
    url: HttpUrl
    events: List[event_type]
    is_active: bool
    retry_count: int
    timeout: int
    created_at: datetime
    updated_at: datetime


class WebhookSubscriptionListResponse(WebhookSubscriptionModel):
    items: List[WebhookSubscriptionResponse]
    total: int


class WebhookSubscriptionAlter(WebhookSubscriptionModel):
    url: HttpUrl | None = None
    events: List[event_type] | None = None
    is_active: bool | None = None
    retry_count: int | None = None
    timeout: int | None = None


class WebhookDeliveryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class WebhookDeliveryCreate(WebhookDeliveryModel):
    subscription_id: int
    event_type: str
    payload: dict


class WebhookDeliveryResponse(WebhookDeliveryModel):
    event_type: str
    payload: dict
    status: str
    attempts: int
    response_status: int | None
    response_body: dict | None
    error_message: str | None
    created_at: datetime
    delivered_at: datetime | None
