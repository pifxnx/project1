import httpx
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from ..celery_app import celery_app, get_session
from ..data.models.webhook import (
    WebhookSubscription,
    WebhookDelivery,
    Status
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

def send_webhook_delivery(hookdel: WebhookDelivery, subscription: WebhookSubscription, session: Session):
    hookdel.attempts += 1

    try:
        with httpx.Client() as client:
            response = client.post(
                url=subscription.url,
                json={
                    "event": hookdel.event_type,
                    "data": hookdel.payload,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                timeout=subscription.timeout
            )
        try:
            response_body = response.json()
        except ValueError:
            response_body = None

        hookdel.response_status = response.status_code
        hookdel.response_body = response_body
        hookdel.status = Status.success if 200 <= response.status_code < 300 else Status.failed
        hookdel.error_message = None

    except httpx.RequestError as e:
        hookdel.status = Status.failed
        hookdel.error_message = str(e)

    if hookdel.status == Status.success:
        hookdel.delivered_at = datetime.now(timezone.utc)

    session.commit()
    session.refresh(hookdel)
    return hookdel


@celery_app.task
def create_webhook_delivery_task(event: str, payload: dict):
    with get_session() as session:
        subs = get_subs_by_event(event, session)

        for sub in subs:
            hookdel = create_webhook_delivery(sub.id, event, payload, session)
            send_webhook_delivery(hookdel, sub, session)