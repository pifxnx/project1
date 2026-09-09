from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List


class WebhookSubscriptionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class WebhookSubscriptionCreate(WebhookSubscriptionModel):
    url: str | None = None
    events: list[str]
    secret_key: str
    retry_count: int | None = None
    timeout: int | None = None 

class WebhookSubscriptionResponse(WebhookSubscriptionModel):
    id: int 
    url: str 
    events: list[str]
    is_active: bool 
    retry_count: int
    timeout: int 
    created_at: datetime
    updated_at: datetime

class WebhookSubscriptionListResponse(WebhookSubscriptionModel):
    items: List[WebhookSubscriptionResponse]
    total: int


class WebhookSubscriptionAlter(WebhookSubscriptionModel):
    url: str | None = None 
    events: list[str] | None = None
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
    response_status: str | None
    response_body: str | None
    error_message: str | None
    created_at: datetime
    delivered_at: datetime | None 
    