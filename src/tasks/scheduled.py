import json
from sqlalchemy import select, update, func, or_
from datetime import datetime, timedelta, timezone
from ..data.models.batch import Batch
from ..data.models.product import Product
from ..data.models.webhook import WebhookDelivery, WebhookSubscription, Status
from ..celery_app import celery_app, get_session
from .webhooks import send_webhook_delivery
from ..core.storage import minio
from ..core.cache import get_redis_sync


@celery_app.task(name="tasks.auto_close_expired_batches")
def auto_close_expired_batches():
    with get_session() as session:
        stmt = (
            update(Batch)
            .where(Batch.shift_end < func.now(), Batch.is_closed == False)
            .values(is_closed=True, closed_at=func.now())
        )
        session.execute(stmt)
        session.commit()

        return


@celery_app.task(name="tasks.cleanup_old_files")
def cleanup_old_files_task():
    t = datetime.now(timezone.utc) - timedelta(days=30)
    buckets = ["reports", "exports", "imports"]

    for bucket in buckets:
        for obj in minio.list_files(bucket):
            if obj.last_modified < t:
                minio.delete_file(bucket, obj.object_name)


@celery_app.task(name="tasks.update_cached_statistics")
def update_cached_statistics():
    with get_session() as session:
        stmt = (
            select(
                func.count(Batch.id.distinct()).label("total_batches"),
                func.count(Batch.id.distinct())
                .filter(Batch.is_closed.is_(False))
                .label("active_batches"),
                func.count(Product.id).label("total_products"),
                func.count(Product.id)
                .filter(Product.is_aggregated.is_(True))
                .label("aggregated_products"),
            )
            .select_from(Batch)
            .outerjoin(Product, Batch.id == Product.batch_id)
        )

        result = session.execute(stmt)
        stats = result.one()

        aggr_rate = (
            stats.aggregated_products / stats.total_products * 100
            if stats.total_products > 0
            else 0
        )

        result = {
            "total_batches": stats.total_batches,
            "active_batches": stats.active_batches,
            "total_products": stats.total_products,
            "aggregated_products": stats.aggregated_products,
            "aggregation_rate": aggr_rate,
            "cached_at": datetime.now(timezone.utc).isoformat(),
        }

    redis = get_redis_sync()
    redis.set("dashboard_stats:", json.dumps(result, default=str), ex=300)
