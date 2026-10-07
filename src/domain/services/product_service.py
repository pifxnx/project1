from ...data.repositories.product_repository import ProductRepository
from ...data.models.product import Product
from ...api.v1.schemas.product import ProductCreate, ProductResponse
from ..exceptions.product_exception import (
    ProductNotFoundException,
    ProductAlreadyExistsException,
)
from ..exceptions.batch_exception import BatchNotFoundException
from asyncpg.exceptions import UniqueViolationError, ForeignKeyViolationError
from ...tasks.aggregation import aggregate_products_task
from ...tasks.webhooks import create_webhook_delivery_task
from ...core.cache import invalidate_batch
from typing import List
from sqlalchemy.exc import IntegrityError


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    async def create(self, data: ProductCreate) -> ProductResponse:
        product = Product(**data.model_dump())
        try:
            product = await self.repository.create(product)
        except IntegrityError as e:
            if isinstance(e.orig.__cause__, UniqueViolationError):
                raise ProductAlreadyExistsException()
            elif isinstance(e.orig.__cause__, ForeignKeyViolationError):
                raise BatchNotFoundException(product.batch_id)
            raise

        await invalidate_batch(product.batch_id)

        return ProductResponse.model_validate(product)

    async def get_by_id(self, product_id: int) -> ProductResponse | None:
        product = await self.repository.get_by_id(product_id)

        if not product:
            raise ProductNotFoundException(product_id)

        return ProductResponse.model_validate(product)

    async def get_by_batch_id(self, batch_id: int) -> List[ProductResponse] | None:
        products = await self.repository.get_by_batch_id(batch_id)

        return [ProductResponse.model_validate(product) for product in products]


class AggregationService:
    def __init__(self, repository: ProductRepository | None = None):
        self.repository = repository

    async def aggregate_products_batch(
        self, batch_id: int, unique_codes: list[str]
    ) -> dict:
        unique_codes = list(dict.fromkeys(unique_codes))
        products = await self.repository.get_by_batch_id_and_unique_codes(
            batch_id, unique_codes
        )

        found = {p.unique_code for p in products}
        errors = [
            {"code": p.unique_code, "reason": "already aggregated"}
            for p in products
            if p.is_aggregated
        ]
        errors += [
            {"code": code, "reason": "product not found"}
            for code in unique_codes
            if code not in found
        ]
        to_aggregate = [p.unique_code for p in products if not p.is_aggregated]

        aggregated = 0
        if to_aggregate:
            aggregated = await self.repository.aggregate_products(
                batch_id, to_aggregate
            )

        result = {
            "total": len(unique_codes),
            "aggregated": aggregated,
            "failed": len(errors),
            "errors": errors,
        }

        await invalidate_batch(batch_id)
        create_webhook_delivery_task.delay("product_aggregated", result)

        return result

    async def aggregate_products_batch_async(
        self, batch_id: int, unique_codes: list[str]
    ) -> dict:
        task = aggregate_products_task.delay(batch_id, unique_codes)

        return {"task_id": task.id}
