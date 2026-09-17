import json
from datetime import datetime, timezone
from redis.asyncio import Redis
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import List
from ..api.v1.schemas.batch import BatchResponse, BatchWithProductsResponse
from ..data.models.batch import Batch
from ..data.models.product import Product
from ..domain.services.batch_service import BatchService
from ..core.database import sessionmaker
from ..core.config import settings


redis = Redis.from_url(settings.redis_url, decode_responses=True)

async def get_redis() -> Redis:
    return redis



def cache(ttl: int, key_prefix: str):
    def deco(func):
        async def wrapper(*args, **kwargs):
            key = f"{key_prefix}:{args}:{kwargs}"

            r = await get_redis()

            cached = await r.get(key)
            if cached is not None:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            data = json.dumps(result, default=str)

            await r.set(key, data, ex=ttl)

            return result
        return wrapper
    return deco


@cache(ttl=300, key_prefix="dashboard_stats")
async def get_dashboard_statistics():
    async with sessionmaker() as session:
        stmt = select(func.count(Batch.id.distinct()).label("total_batches"),
                    func.count(Batch.id.distinct())
                                .filter(Batch.is_closed.is_(False))
                                .label("active_batches"),
                        func.count(Product.id).label("total_products"),
                        func.count(Product.id).filter(Product.is_aggregated.is_(True))
                                    .label("aggregated_products")
                        ).select_from(Batch).outerjoin(Product, Batch.id == Product.batch_id)

        result = await session.execute(stmt)
        stats = result.one()

        aggr_rate = stats.aggregated_products / stats.total_products * 100 if stats.total_products > 0 else 0

        return {
            "total_batches": stats.total_batches,
            "active_batches": stats.active_batches,
            "total_products": stats.total_products,
            "aggregated_products": stats.aggregated_products,
            "aggregation_rate": aggr_rate,
            "cached_at": datetime.now(timezone.utc).isoformat()
            }


@cache(ttl=60, key_prefix="batches_list")
async def get_batches_list(
    is_closed: bool | None = None,
    offset: int = 0,
    limit: int = 20
) -> List[dict]:
    async with sessionmaker() as session:
        stmt = (select(Batch).limit(limit).offset(offset))

        if is_closed is not None:
            stmt = stmt.where(Batch.is_closed == is_closed)

        result = await session.execute(stmt)
        batches = result.scalars().all()

        batches = [BatchResponse.model_validate(batch)
                for batch in batches]

        return [batch.model_dump(mode="json")
                for batch in batches]


@cache(ttl=600, key_prefix="batch_detail")
async def get_batch_with_products(batch_id: int):
    async with sessionmaker() as session:
        stmt = (select(Batch).where(Batch.id == batch_id)
                .options(joinedload(Batch.products)))

        result = await session.execute(stmt)
        batch = result.unique().scalar_one_or_none()
        if batch is None:
            return None
        batch = BatchWithProductsResponse.model_validate(batch)

        return batch.model_dump(mode="json")