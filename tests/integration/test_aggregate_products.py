from sqlalchemy import select
from src.data.models.product import Product
from src.data.repositories.product_repository import ProductRepository
from src.domain.services.product_service import ProductService


async def test_aggregate_product(get_test_db, create_product):
    product = await create_product("test_123")
    repository = ProductRepository(get_test_db)
    service = ProductService(repository)

    result = await service.aggregate_products_batch(
        batch_id=product.batch_id,
        unique_codes=[product.unique_code]
    )

    assert result["success"] is True
    assert result["total"] == 1
    assert result["aggregated"] == 1
    assert result["failed"] == 0
    assert result["errors"] == []

    stmt = select(Product).where(Product.id == product.id)

    result = await get_test_db.execute(stmt)
    product = result.scalar_one()

    assert product.is_aggregated is True
    assert product.aggregated_at is not None


async def test_multiple_products(get_test_db, create_product):
    p1 = await create_product("test_124")
    p2 = await create_product("test_125")

    p2.is_aggregated = True
    await get_test_db.commit()

    repository = ProductRepository(get_test_db)
    service = ProductService(repository)

    result = await service.aggregate_products_batch(
        batch_id=p1.batch_id,
        unique_codes=[
            p1.unique_code,
            p2.unique_code,
            "test_000"
        ]
    )

    assert result["total"] == 3
    assert result["aggregated"] == 1
    assert result["failed"] == 2