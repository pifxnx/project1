from sqlalchemy import select, update, func
from datetime import datetime, timedelta, timezone
from ..data.models.batch import Batch
from ..data.models.product import Product
from ..data.models.webhook import (
    WebhookDelivery, WebhookSubscription, Status
)
from ..celery_app import celery_app, get_session
from .webhooks import send_webhook_delivery
from ..core.storage import minio


@celery_app.task(name="tasks.auto_close_expired_batches")
def auto_close_expired_batches():
    with get_session() as session:
        stmt = (update(Batch)
                .where(Batch.shift_end < func.now(),
                       Batch.is_closed == False)
                .values(is_closed = True, closed_at=func.now()))
        session.execute(stmt)
        session.commit()

        return


@celery_app.task(name="tasks.retry_failed_webhooks")
def retry_failed_webhook_task():
    with get_session() as session:
        stmt = (select(WebhookDelivery)
                .join(WebhookSubscription)
                .where(WebhookDelivery.status==Status.failed))
        hookdels = session.execute(stmt).scalars().all()

        for hookdel in hookdels:
            sub = hookdel.subscription
            send_webhook_delivery(hookdel, sub, session)


@celery_app.task(name="tasks.cleanup_old_files")
def cleanup_old_files_task():
    t = datetime.now(timezone.utc) - timedelta(days=30)
    buckets = ["reports", "exports", "imports"]

    for bucket in buckets:
        for obj in minio.list_files(bucket):
            if obj.last_modified < t:
                minio.delete_file(bucket, obj.object_name)
