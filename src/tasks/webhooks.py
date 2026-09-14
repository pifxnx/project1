import httpx
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from ..celery_app import celery_app, get_session
from ..data.models.webhook import (
    WebhookSubscription,
    WebhookDelivery
)


def get_subs_by_event(event: str, session: Session) -> List[WebhookSubscription]:
    stmt = (select(WebhookSubscription)
            .where(WebhookSubscription.events.contains([event])))
    result = session.execute(stmt)

    return list(result.scalars().all())

def create_webhook_delivery(sub_id: int, event: str, payload: dict, session: Session) -> WebhookDelivery:
    hookdel = WebhookDelivery(
        subscription_id=sub_id,
        event_type=event,
        payload=payload
    )
    session.add(hookdel)
    session.commit()
    session.refresh(hookdel)

    return hookdel


@celery_app.task
def create_webhook_delivery_task(event: str, payload: dict):
    with get_session() as session:
        subs = get_subs_by_event(event, session)

        with httpx.Client() as client:
            for sub in subs:
                hookdel = create_webhook_delivery(
                    sub.id, event, payload, session
                )

                try:
                    response = client.post(
                        url=sub.url,
                        json={
                            "event": event,
                            "data": payload,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        },
                        timeout=sub.timeout
                    )
                    try:
                        response_body = response.json()
                    except ValueError:
                        response_body = None
                    stmt = (update(WebhookDelivery)
                            .where(WebhookDelivery.id == hookdel.id)
                            .values(response_status=response.status_code,
                                    response_body=response_body,
                                    status="success" if 200 <= response.status_code < 300 else "failed"))

                except httpx.RequestError as e:
                    stmt = (update(WebhookDelivery)
                            .where(WebhookDelivery.id == hookdel.id)
                            .values(status="failed", error_message=str(e)))

                session.execute(stmt)
                session.commit()
                session.refresh(hookdel)