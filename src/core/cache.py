import json
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List
from ..api.v1.schemas.batch import BatchResponse, BatchWithProductsResponse
from ..data.models.batch import Batch
from ..domain.services.batch_service import BatchService
from ..core.database import sessionmaker


redis = Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

async def get_redis() -> Redis:
    return redis



def cache(ttl: int, key_prefix: str):
    def deco(func):
        async def wrapper(**kwargs):
            key = f"{key_prefix}:{kwargs}"

            r = await get_redis()

            cached = await r.get(key)
            if cached is not None:
                return json.loads(cached)

            result = await func(**kwargs)
            data = json.dumps(result)

            await r.set(key, data, ex=ttl)

            return result
        return wrapper
    return deco


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
        batch = result.scalar_one_or_none()
        if batch is None:
            return None
        batch = BatchWithProductsResponse.model_validate(batch)

        return batch.model_dump(mode="json")