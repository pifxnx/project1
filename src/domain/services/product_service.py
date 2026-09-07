from ...data.repositories.product_repository import ProductRepository
from ...data.models.product import Product
from ...api.v1.schemas.product import ProductCreate, ProductResponse
from ..exceptions.product_exception import (
    ProductNotFoundException,
    ProductAlreadyExistsException
)
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

    async def aggregate_products_batch(
            self,
            batch_id: int,
            unique_codes: list[str]
    ) -> dict:
        products = await self.repository.get_by_batch_id_and_unique_codes(
            batch_id, unique_codes
        )

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

        missing_codes = requested_codes - found_codes

        for code in missing_codes:
            errors.append(
                {"code": code, "reason": "product not found"}
            )

        aggregated = 0

        if codes_to_aggregate:
            aggregated = await self.repository.aggregate_products(
                batch_id,
                codes_to_aggregate
            )

        failed = len(errors)

        return {
            "success": True,
            "total": len(unique_codes),
            "aggregated": aggregated,
            "failed": failed,
            "errors": errors
        }