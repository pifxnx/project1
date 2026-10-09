import pytest
from sqlalchemy.engine import create
from sqlalchemy.exc import IntegrityError
from src.data.repositories.product_repository import ProductRepository
from src.data.models.product import Product
from tests.conftest import create_batch


@pytest.mark.asyncio
async def test_get_product_by_batch_id(get_test_db, create_batch, create_product):
    batch = await create_batch(batch_number=22)

    await create_product(unique_code="code1", batch_id=batch.id)
    await create_product(unique_code="code2", batch_id=batch.id)

    repository = ProductRepository(get_test_db)

    products = await repository.get_by_batch_id(batch.id)

    assert len(products) == 2
    assert {p.unique_code for p in products} == {"code1", "code2"}
    assert {p.batch_id for p in products} == {batch.id}


@pytest.mark.asyncio
async def test_get_product_by_id(get_test_db, create_batch, create_product):
    repository = ProductRepository(get_test_db)

    batch = await create_batch(batch_number=33)
    product = await create_product(unique_code="code3", batch_id=batch.id)

    p = await repository.get_by_id(product.id)

    assert p is not None
    assert p.unique_code == "code3"
    assert p.batch_id == batch.id


@pytest.mark.asyncio
async def test_create_product(get_test_db, create_batch):
    repository = ProductRepository(get_test_db)

    batch = await create_batch(batch_number=44)
    product = await repository.create(
        Product(
            unique_code="code4",
            batch_id=batch.id,
        )
    )

    assert product is not None
    assert product.unique_code == "code4"
    assert product.batch_id == batch.id


@pytest.mark.asyncio
async def test_create_product_duplicate_unique_code(get_test_db, create_batch):
    repository = ProductRepository(get_test_db)

    batch = await create_batch(batch_number=14)
    await repository.create(Product(unique_code="code5", batch_id=batch.id))

    with pytest.raises(IntegrityError):
        await repository.create(Product(unique_code="code5", batch_id=batch.id))


@pytest.mark.asyncio
async def test_get_product_by_id_not_found(get_test_db):
    repository = ProductRepository(get_test_db)

    p = await repository.get_by_id(9999)

    assert p is None


@pytest.mark.asyncio
async def test_get_products_by_batch_id_not_found(get_test_db, create_batch):
    batch = await create_batch(batch_number=11)

    repository = ProductRepository(get_test_db)

    products = await repository.get_by_batch_id(batch.id)

    assert products == []
