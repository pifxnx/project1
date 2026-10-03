import httpx
import json
import time
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from ..celery_app import celery_app, get_session
from ..data.models.webhook import WebhookSubscription, WebhookDelivery, Status
from ..utils.hmac_util import sign_payload


def get_subs_by_event(event: str, session: Session) -> List[WebhookSubscription]:
    stmt = select(WebhookSubscription).where(
        WebhookSubscription.events.contains([event]),
        WebhookSubscription.is_active.is_(True),
    )
    result = session.execute(stmt)

    return list(result.scalars().all())


def create_webhook_delivery(
    sub_id: int, event: str, payload: dict, session: Session
) -> WebhookDelivery:
    hookdel = WebhookDelivery(subscription_id=sub_id, event_type=event, payload=payload)
    session.add(hookdel)
    session.commit()
    session.refresh(hookdel)

    return hookdel


def send_webhook_delivery(
    hookdel: WebhookDelivery, subscription: WebhookSubscription, session: Session
):
    body_dict = {
        "event": hookdel.event_type,
        "data": hookdel.payload,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    body_bytes = json.dumps(body_dict, default=str).encode("utf-8")
    signature = sign_payload(subscription.secret_key, body_bytes)

    max_attempts = subscription.retry_count
    with httpx.Client() as client:
        for attempt in range(1, max_attempts + 1):
            hookdel.attempts += 1
            try:
                response = client.post(
                    url=subscription.url,
                    content=body_bytes,
                    headers={
                        "Content-Type": "application/json",
                        "X-Signature": f"sha256={signature}",
                    },
                    timeout=subscription.timeout,
                )
                try:
                    response_body = response.json()
                except ValueError:
                    response_body = None

                hookdel.response_status = response.status_code
                hookdel.response_body = response_body
                hookdel.error_message = None

                if 200 <= response.status_code < 300:
                    hookdel.status = Status.success
                    hookdel.delivered_at = datetime.now(timezone.utc)
                    break
                else:
                    hookdel.status = Status.failed
                    if response.status_code < 500:
                        break

            except httpx.RequestError as e:
                hookdel.status = Status.failed
                hookdel.error_message = str(e)

            if attempt < max_attempts:
                time.sleep(2 ** (attempt - 1))

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
