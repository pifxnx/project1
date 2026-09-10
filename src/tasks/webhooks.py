import httpx
import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from ..core.config import settings 
from ..celery_app import celery_app
from ..data.models.webhook import WebhookDelivery
from ..data.repositories.webhook_repository import (
    WebhookDeliveryRepository,
    WebhookSubscriptionRepository
)

@celery_app.task
def create_webhook_delivery(event: str, payload: dict):
    return asyncio.run(
        _create_webhook_delivery(event, payload)
    )



async def _create_webhook_delivery(event: str, payload: dict):
    engine = create_async_engine(settings.db_url)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with sessionmaker() as session:
            repository = WebhookSubscriptionRepository(session)
            subs = await repository.get_by_event(event)

            repository = WebhookDeliveryRepository(session)
            async with httpx.AsyncClient() as client:
                for sub in subs:
                    delivery = await repository.create(
                        WebhookDelivery(
                            subscription_id=sub.id,
                            event_type=event,
                            payload=payload
                        )
                    )

                    response = await client.post(
                        url=sub.url,
                        json={
                            "event": event,
                            "data": payload,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    )

                    result = await repository.update(
                        delivery_id=delivery.id,
                        response_status=response.status_code,
                        response_body=response.json(),
                        status="success" if 200 <= response.status_code < 300 else "failed"
                    )
    finally:
        await engine.dispose()