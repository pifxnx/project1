from sqlalchemy import select
from src.data.models.product import Product
from src.data.repositories.product_repository import ProductRepository
from src.domain.services.product_service import ProductService


async def test_aggregate_product(get_test_db, create_product):
    repository = ProductRepository(get_test_db)
    service = ProductService(repository)

    result = await service.aggregate_products_batch(
        batch_id=create_product.batch_id,
        unique_codes=[create_product.unique_code]
    )

    assert result["success"] is True
    assert result["total"] == 1
    assert result["aggregated"] == 1
    assert result["failed"] == 0
    assert result["errors"] == []

    stmt = select(Product).where(Product.id == create_product.id)

    result = await get_test_db.execute(stmt)
    product = result.scalar_one()

    assert product.is_aggregated is True
    assert product.aggregated_at is not None