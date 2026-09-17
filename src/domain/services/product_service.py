from ...data.repositories.product_repository import ProductRepository
from ...data.models.product import Product
from ...api.v1.schemas.product import ProductCreate, ProductResponse
from ..exceptions.product_exception import (
    ProductNotFoundException,
    ProductAlreadyExistsException
)
from ...tasks.aggregation import aggregate_products_task
from ...tasks.webhooks import create_webhook_delivery_task
from typing import List


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    async def create(self, data: ProductCreate) -> ProductResponse:
        product = Product(**data.model_dump())
        product = await self.repository.create(product)
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
    async def aggregate_products_batch(
            self,
            batch_id: int,
            unique_codes: list[str]
    ) -> dict:
        result = aggregate_products_task.delay(batch_id, unique_codes)
        create_webhook_delivery_task.delay(
            "product_aggregated",
            {"batch_id": batch_id,
             "unique_codes": unique_codes}
        )

        return {"id": result.id,
                "status": result.status}