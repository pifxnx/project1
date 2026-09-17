from sqlalchemy import select, update
from datetime import datetime, timezone
from ..celery_app import celery_app, get_session
from .webhooks import create_webhook_delivery_task
from ..data.models.product import Product


@celery_app.task
def aggregate_products_task(batch_id: int, unique_codes: list[str]) -> dict:
    with get_session() as session:
        stmt = select(Product).where(Product.batch_id == batch_id,
                                     Product.unique_code.in_(unique_codes))
        products = session.execute(stmt).scalars().all()

        requested_codes = set(unique_codes)
        found_codes = set()
        codes_to_aggregate = []
        errors = []

        for product in products:
            found_codes.add(product.unique_code)
            if product.is_aggregated:
                errors.append({"code": product.unique_code,
                               "reason": "already aggregated"})
            else:
                codes_to_aggregate.append(product.unique_code)

        for code in requested_codes - found_codes:
            errors.append({"code": code, "reason": "product not found"})

        aggregated = 0
        if codes_to_aggregate:
            stmt = (update(Product)
                    .where(Product.batch_id == batch_id,
                            Product.unique_code.in_(codes_to_aggregate),
                            Product.is_aggregated.is_(False))
                            .values(is_aggregated=True, aggregated_at=datetime.now(timezone.utc))
                            .returning(Product.id))
            result = session.execute(stmt)
            session.commit()
            aggregated = len(result.scalars().all)

        result = {
            "total": len(unique_codes),
            "aggregated": aggregated,
            "failed": len(errors),
            "errors": errors
        }

        create_webhook_delivery_task.delay(
            "aggregation",
            "result": **result
        )

        return result
