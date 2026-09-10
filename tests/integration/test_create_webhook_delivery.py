import pytest
from src.data.models.webhook import WebhookSubscription, WebhookDelivery
from src.api.v1.schemas.webhook import WebhookSubscriptionCreate
from src.api.v1.schemas.batch import BatchCreate
from src.data.repositories.webhook_repository import (
    WebhookSubscriptionRepository,
    WebhookDeliveryRepository
)
from src.domain.services.webhook_service import (
    WebhookSubscriptionService,
    WebhookDeliveryService
)
from src.tasks.webhooks import _create_webhook_delivery


@pytest.mark.asyncio
async def test_create_webhook_delivery(get_test_db, create_subscription, create_batch):
    payload = {
        "id": create_batch.id,
        "batch_number": create_batch.batch_number,
        "batch_date": create_batch.batch_date.isoformat(),
        "nomenclature": create_batch.nomenclature,
        "work_center": create_batch.work_center_id
    }
    await _create_webhook_delivery("batch_created", payload)
    sub = create_subscription
    repository = WebhookDeliveryRepository(get_test_db)

    deliveries = await repository.get_by_sub_id(sub.id)
    delivery = deliveries[0]

    assert delivery.payload == payload
    assert delivery.event_type == "batch_created"
    assert delivery.response_status == 200