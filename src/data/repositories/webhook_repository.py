from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..models.webhook import WebhookSubscription, WebhookDelivery


class WebhookSubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, hooksub: WebhookSubscription) -> WebhookSubscription:
        self.session.add(hooksub)
        await self.session.commit()
        await self.session.refresh(hooksub)

        return hooksub

    async def get_by_id(self, sub_id: int) -> WebhookSubscription | None:
        hooksub = await self.session.get(WebhookSubscription, sub_id)
        return hooksub


class WebhookDeliveryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, hookdelivery: WebhookDelivery) -> WebhookDelivery:
        self.session.add(hookdelivery)
        await self.session.commit()
        await self.session.refresh(hookdelivery)

        return hookdelivery

    async def get_by_id(self, delivery_id: int) -> WebhookDelivery | None:
        hookdelivery = await self.session.get(WebhookDelivery, delivery_id)
        return hookdelivery

    async def get_by_sub_id(self, sub_id: int) -> List[WebhookDelivery]:
        stmt = (select(WebhookDelivery)
                    .where(WebhookDelivery.subscription_id == sub_id))
        result = await self.session.execute(stmt)

        return list(result.scalars().all())