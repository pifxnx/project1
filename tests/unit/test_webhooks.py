from unittest.mock import AsyncMock

import pytest

from src.api.v1.schemas.webhook import (
    WebhookSubscriptionCreate,
    WebhookSubscriptionAlter,
)
from src.data.models.webhook import WebhookSubscription
from src.domain.exceptions.webhook_excpetion import WebhookSubscriptionNotFoundException
from src.domain.services.webhook_service import WebhookSubscriptionService


@pytest.mark.asyncio
async def test_subscription_service_create():
    repository = AsyncMock()
    repository.create.return_value = WebhookSubscription(
        id=1,
        url="http://example.com/hook",
        events=["batch_created"],
        is_active=True,
    )

    service = WebhookSubscriptionService(repository)

    result = await service.create(
        WebhookSubscriptionCreate(
            url="http://example.com/hook",
            events=["batch_created"],
        )
    )

    assert result.id == 1
    assert result.url == "http://example.com/hook"


@pytest.mark.asyncio
async def test_subscription_service_get_by_id_not_found():
    repository = AsyncMock()
    repository.get_by_id.return_value = None

    service = WebhookSubscriptionService(repository)

    with pytest.raises(WebhookSubscriptionNotFoundException):
        await service.get_by_id(999)


@pytest.mark.asyncio
async def test_subscription_service_delete_not_found():
    repository = AsyncMock()
    repository.delete.return_value = False

    service = WebhookSubscriptionService(repository)

    with pytest.raises(WebhookSubscriptionNotFoundException):
        await service.delete(999)

