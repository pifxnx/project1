from sqlalchemy import select, update
from datetime import datetime, timezone
from ..celery_app import celery_app, get_session
from .webhooks import create_webhook_delivery_task
from ..data.models.product import Product
from ..core.cache import invalidate_batch_sync


CHUNK_SIZE = 20


def publish_progress(task, current: int, total: int, aggregated: int) -> None:
    if task.request.id:
        task.update_state(
            state="PROGRESS",
            meta={"current": current, "total": total, "aggregated": aggregated},
        )


@celery_app.task(bind=True)
def aggregate_products_task(self, batch_id: int, unique_codes: list[str]) -> dict:
    with get_session() as session:
        stmt = select(Product).where(
            Product.batch_id == batch_id, Product.unique_code.in_(unique_codes)
        )
        products = session.execute(stmt).scalars().all()

        requested_codes = set(unique_codes)
        found_codes = set()
        codes_to_aggregate = []
        errors = []

        for product in products:
            found_codes.add(product.unique_code)
            if product.is_aggregated:
                errors.append(
                    {"code": product.unique_code, "reason": "already aggregated"}
                )
            else:
                codes_to_aggregate.append(product.unique_code)

        for code in requested_codes - found_codes:
            errors.append({"code": code, "reason": "product not found"})

        total = len(unique_codes)
        processed = len(errors)
        aggregated = 0
        publish_progress(self, processed, total, aggregated)

        for i in range(0, len(codes_to_aggregate), CHUNK_SIZE):
            chunk = codes_to_aggregate[i : i + CHUNK_SIZE]
            stmt = (
                update(Product)
                .where(
                    Product.batch_id == batch_id,
                    Product.unique_code.in_(chunk),
                    Product.is_aggregated.is_(False),
                )
                .values(is_aggregated=True, aggregated_at=datetime.now(timezone.utc))
                .returning(Product.id)
            )
            result = session.execute(stmt)
            session.commit()
            aggregated += len(result.scalars().all())
            processed += len(chunk)
            publish_progress(self, processed, total, aggregated)

        result = {
            "total": len(unique_codes),
            "aggregated": aggregated,
            "failed": len(errors),
            "errors": errors,
        }

        invalidate_batch_sync(batch_id)

        create_webhook_delivery_task.delay("product_aggregated", result)

        return result
