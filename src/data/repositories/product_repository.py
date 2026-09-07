from ..models.product import Product
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select, update
from typing import List
from datetime import datetime, timezone


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

    async def get_by_batch_id_and_unique_codes(
            self,
            batch_id: int,
            unique_codes: list[str]
    ) -> List[Product]:
        stmt = select(Product).where(Product.batch_id == batch_id,
                                    Product.unique_code.in_(unique_codes))
        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def aggregate_products(
            self,
            batch_id: int,
            unique_codes: list[str]
    ) -> int:
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
            .returning(Product.id)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return len(result.scalars().all())