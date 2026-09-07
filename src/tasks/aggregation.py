import asyncio
from ..celery_app import celery_app
from ..core.database import sessionmaker
from ..data.repositories.product_repository import ProductRepository
from ..domain.services.product_service import ProductService

@celery_app.task
def aggregate_products_batch_task(
    batch_id: int,
    unique_codes: list[str]
):
    return asyncio.run(
        _aggregate_products_batch(
            batch_id,
            unique_codes
        )
    )


async def _aggregate_products_batch(
        batch_id: int,
        unique_codes: list[str]
):
    async with sessionmaker() as session:
        repository = ProductRepository(session)
        service = ProductService(repository)

        return await service.aggregate_products_batch(
            batch_id,
            unique_codes
        )