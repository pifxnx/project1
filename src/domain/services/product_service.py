from ...data.repositories.product_repository import ProductRepository
from ...data.models.product import Product
from ...api.v1.schemas.product import ProductCreate, ProductResponse
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

        ## написать исключение если не найдено

        return ProductResponse.model_validate(product)

    async def get_by_batch_id(self, batch_id: int) -> List[ProductResponse] | None:
        products = await self.repository.get_by_batch_id(batch_id)

        ## написать исключение если не найдено

        return [ProductResponse.model_validate(product) for product in products]