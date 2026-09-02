from ..models.product import Product
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select
from typing import List


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session 

    async def create(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)

        return product

    async def get_by_id(self, product_id: int) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()


    async def get_by_batch_id(self, batch_id: int) -> List[Product]:
        stmt = select(Product).where(Product.batch_id == batch_id)
        result = await self.session.execute(stmt)

        return list(result.scalars().all())