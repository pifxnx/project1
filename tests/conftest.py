import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy import text
from src.data.models.work_center import WorkCenter
from src.data.models.batch import Batch
from src.data.models.product import Product

TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/test"


@pytest_asyncio.fixture
async def get_test_db():
    engine = create_async_engine(TEST_DB_URL)

    sessionmaker = async_sessionmaker(
        engine,
        expire_on_commit=False
    )

    async with sessionmaker() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def truncate_tables(get_test_db):
    await get_test_db.execute(text(
        "TRUNCATE work_centers, batches, products RESTART IDENTITY"
    ))
    await get_test_db.commit()



@pytest_asyncio.fixture
async def create_work_center(get_test_db):
    workcenter = WorkCenter(
        identifier='wc_test',
        name="test_work_center"
    )

    get_test_db.add(workcenter)
    await get_test_db.commit()
    await get_test_db.refresh(workcenter)

    return workcenter


@pytest_asyncio.fixture
async def create_batch(get_test_db, create_work_center):
    batch = Batch(
        task_description="test_batch1",
        work_center_id=create_work_center.id,
        shift="test_shift",
        team="test_team",
        batch_number=1,
        nomenclature="test_nomenclature",
        ekn_code="test_code"
    )

    get_test_db.add(batch)
    await get_test_db.commit()
    await get_test_db.refresh(batch)

    return batch


@pytest_asyncio.fixture
async def create_product(get_test_db, create_batch):
    product = Product(
        unique_code="test_123",
        batch_id=create_batch.id
    )

    get_test_db.add(product)
    await get_test_db.commit()
    await get_test_db.refresh(product)

    return product