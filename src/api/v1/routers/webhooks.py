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
    WebhookSubscriptionAlter,
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

    return await service.create(hooksub)

@router.get("/", response_model=List[WebhookSubscriptionResponse])
async def get_webhook_subscriptions(
    session: Annotated[AsyncSession, Depends(get_db)]
):
    repository = WebhookSubscriptionRepository(session)
    service = WebhookSubscriptionService(repository)

    return await service.get_all()

@router.patch("/{webhook_id}", response_model=WebhookSubscriptionResponse)
async def alter_webhook(
    session: Annotated[AsyncSession, Depends(get_db)],
    webhook_id: int,
    data: WebhookSubscriptionAlter
):
    repository = WebhookSubscriptionRepository(session)
    service = WebhookSubscriptionService(repository)

    return await service.alter(webhook_id, data)

@router.delete("/{webhook_id}")
async def delete_webhook(
    session: Annotated[AsyncSession, Depends(get_db)],
    webhook_id: int
):
    repository = WebhookSubscriptionRepository(session)
    service = WebhookSubscriptionService(repository)

    await service.delete(webhook_id)