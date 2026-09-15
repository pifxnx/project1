import pytest_asyncio
import pytest
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.data.models.work_center import WorkCenter
from src.data.models.batch import Batch
from src.data.models.product import Product
from src.data.models.webhook import WebhookSubscription

TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/test"
TEST_DB_URL_SYNC = "postgresql+psycopg2://postgres:postgres@localhost:5433/test"


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


@pytest.fixture
def get_test_db_sync():
    engine = create_engine(TEST_DB_URL_SYNC)
    session_maker = sessionmaker(engine, expire_on_commit=False)

    with session_maker() as session:
        yield session

    engine.dispose()

@pytest.fixture
def patch_get_session(monkeypatch, get_test_db_sync):
    monkeypatch.setattr("src.tasks.webhooks.get_session", lambda: get_test_db_sync)

@pytest_asyncio.fixture(autouse=True)
async def truncate_tables(get_test_db):
    await get_test_db.execute(text(
        "TRUNCATE work_centers, batches, products, webhook_subscriptions, webhook_deliveries RESTART IDENTITY"
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
async def create_subscription(get_test_db):
    sub = WebhookSubscription(events=["batch_created"])
    get_test_db.add(sub)
    await get_test_db.commit()
    await get_test_db.refresh(sub)

    return sub


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
    async def _create_product(unique_code: str):
        product = Product(
            unique_code=unique_code,
            batch_id=create_batch.id
        )

        get_test_db.add(product)
        await get_test_db.commit()
        await get_test_db.refresh(product)

        return product

    return _create_product