from unittest.mock import AsyncMock
from src.domain.services.product_service import ProductService
from src.data.models.product import Product
import pytest


@pytest.mark.asyncio
async def test_already_aggregated():
    repository = AsyncMock()
    repository.get_by_batch_id_and_unique_codes.return_value = [
        Product(
            id=1,
            unique_code="test_123",
            batch_id=1,
            is_aggregated=True
        )
    ]

    service = ProductService(repository)

    result = await service.aggregate_products_batch(
        batch_id=1,
        unique_codes=["test_123"]
    )

    assert result["total"] == 1
    assert result["aggregated"] == 0
    assert result["failed"] == 1
    assert result["errors"] == [
        {"code": "test_123", "reason": "already aggregated"}
    ]