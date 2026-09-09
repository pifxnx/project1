import httpx
import asyncio
from datetime import datetime, timezone
from ..celery_app import celery_app
from ..data.models.webhook import WebhookDelivery
from ..core.database import sessionmaker
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





    # id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # subscription_id: Mapped[int] = mapped_column(ForeignKey("webhook_subscriptions.id"))
    # event_type: Mapped[str]
    # payload: Mapped[dict] = mapped_column(JSON)

    # status: Mapped[str] = mapped_column(Enum(Status), default=Status.pending)
    # attempts: Mapped[int] = mapped_column(default=0)
    # response_status: Mapped[str | None]
    # response_body: Mapped[str | None]
    # error_message: Mapped[str | None]

    # created_at: Mapped[datetime] = mapped_column(
    #     DateTime(timezone=True),
    #     default=lambda: datetime.now(timezone.utc)
    # )
    # delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))