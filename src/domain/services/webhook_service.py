from typing import List
from ...data.repositories.webhook_repository import(
    WebhookDeliveryRepository,
    WebhookSubscriptionRepository
)
from ...api.v1.schemas.webhook import(
    WebhookDeliveryResponse,
    WebhookDeliveryCreate,
    WebhookSubscriptionResponse,
    WebhookSubscriptionCreate
)
from ...data.models.webhook import(
    WebhookDelivery,
    WebhookSubscription
)


class WebhookSubscriptionService:
    def __init__(self, repository: WebhookSubscriptionRepository):
        self.repository = repository 

    async def create(self, data: WebhookSubscriptionCreate) -> WebhookSubscriptionResponse:
        hooksub = WebhookSubscription(**data.model_dump())
        hooksub = await self.repository.create(hooksub)

        return WebhookSubscriptionResponse.model_validate(hooksub)

    async def get_by_id(self, sub_id: int) -> WebhookSubscriptionResponse | None:
        hooksub = await self.repository.get_by_id(sub_id)

        return WebhookSubscriptionResponse.model_validate(hooksub)


class WebhookDeliveryService:
    def __init__(self, repository: WebhookDeliveryRepository):
        self.repository = repository 

    async def create(self, data: WebhookDeliveryCreate) -> WebhookDeliveryResponse:
        hookdel = WebhookDelivery(**data.model_dump())
        hookdel = await self.repository.create(hookdel)

        return WebhookDeliveryResponse.model_validate(hookdel)

    async def get_by_id(self, del_id: int) -> WebhookDeliveryResponse | None:
        hookdel = await self.repository.get_by_id(del_id)

        return WebhookDeliveryResponse.model_validate(hookdel)

    async def get_by_sub_id(self, sub_id: int) -> List[WebhookDeliveryResponse]:
        hookdels = await self.repository.get_by_sub_id(sub_id)

        return [WebhookDeliveryResponse.model_validate(hookdel)
                for hookdel in hookdels]
