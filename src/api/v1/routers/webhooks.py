from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from ....core.database import get_db
from ....data.repositories.webhook_repository import (
    WebhookSubscriptionRepository,
    WebhookDeliveryRepository
)
from ....domain.services.webhook_service import (
    WebhookSubscriptionService,
    WebhookDeliveryService
)
from ..schemas.webhook import (
    WebhookSubscriptionCreate,
    WebhookSubscriptionResponse,
    WebhookDeliveryCreate,
    WebhookDeliveryResponse
)

router = APIRouter(prefix='/webhooks', tags=["webhooks"])

@router.post("/", response_model=WebhookSubscriptionResponse)
async def create_webhook_subscription(
    hooksub: WebhookSubscriptionCreate,
    session: Annotated[AsyncSession, Depends(get_db)]
):
    repository = WebhookSubscriptionRepository(session)
    service = WebhookSubscriptionService(repository)

    return service.create(hooksub)

@router.get("/", response_model=List[WebhookSubscriptionResponse])
async def get_webhook_subscriptions(
    session: Annotated[AsyncSession, Depends(get_db)]
):
    repository = WebhookSubscriptionRepository(session)
    service = WebhookSubscriptionService(repository)

    return service.get_all()