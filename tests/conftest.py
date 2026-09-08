import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/test"

engine = create_async_engine(TEST_DB_URL)

test_sessionmaker = async_sessionmaker(
    engine,
    expire_on_commit=False
)

@pytest_asyncio.fixture
async def get_test_db():
    async with test_sessionmaker() as session:
        yield session