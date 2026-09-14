from sqlalchemy import update
from datetime import datetime, timezone
from ..celery_app import session_local, celery_app
from ..data.models.product import Product

@celery_app.task
def aggregate_products_task(batch_id: int, unique_codes: list[str]):
    with session_local() as session:
        stmt = (update(Product)
                .where(
                    Product.batch_id == batch_id,
                    Product.unique_code.in_(unique_codes),
                    Product.is_aggregated.is_(False)
                )
                .values(
                    is_aggregated=True,
                    aggregated_at=datetime.now(timezone.utc)
                )
                .returning(Product.id))

        result = session.execute(stmt)
        session.commit()

        return len(result.scalars().all())