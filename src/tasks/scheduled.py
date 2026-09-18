from sqlalchemy import select, update, func
from ..data.models.batch import Batch
from ..data.models.webhook import (
    WebhookDelivery, WebhookSubscription, Status
)
from ..celery_app import celery_app, get_session
from .webhooks import send_webhook_delivery


@celery_app.task
def auto_close_expired_batches(name="tasks.auto_close_expired_batches"):
    with get_session() as session:
        stmt = (update(Batch)
                .where(Batch.shift_end < func.now(),
                       Batch.is_closed == False)
                .values(is_closed = True, closed_at=func.now()))
        session.execute(stmt)
        session.commit()

        return


@celery_app.task
def retry_failed_webhook_task(name="tasks.retry_failed_webhooks"):
    with get_session() as session:
        stmt = (select(WebhookDelivery)
                .join(WebhookSubscription)
                .where(WebhookDelivery.status==Status.failed))
        hookdels = session.execute(stmt).scalars().all()

        for hookdel in hookdels:
            sub = hookdel.subscription
            send_webhook_delivery(hookdel, sub, session)

