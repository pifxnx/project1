from unittest.mock import AsyncMock
from src.domain.services.product_service import ProductService, AggregationService
from src.data.models.product import Product
import pytest


from unittest.mock import patch, MagicMock
import pytest
from src.domain.services.product_service import AggregationService


@pytest.mark.asyncio
async def test_aggregate_products_batch_delegates_to_celery():
    mock_result = MagicMock(id="task-123", status="PENDING")

    with patch(
        "src.domain.services.product_service.aggregate_products_task"
    ) as mock_task:
        mock_task.delay.return_value = mock_result

        service = AggregationService()
        result = await service.aggregate_products_batch(
            batch_id=1,
            unique_codes=["test_123"]
        )

        mock_task.delay.assert_called_once_with(1, ["test_123"])
        assert result == {"id": "task-123", "status": "PENDING"}