import pytest
from unittest.mock import Mock
from src.domain.services.product_service import AggregationService


@pytest.mark.asyncio
async def test_aggregation_service(monkeypatch):
    mock_task = Mock()
    mock_task.delay.return_value.id = "test123"
    mock_task.delay.return_value.status = "pending"

    monkeypatch.setattr(
        "src.domain.services.product_service.aggregate_products_task", mock_task
    )

    service = AggregationService()

    result = await service.aggregate_products_batch(
        batch_id=1, unique_codes=["code1", "code2"]
    )

    mock_task.delay.assert_called_once_with(batch_id=1, unique_codes=["code1", "code2"])

    assert result == {"id": "test123", "status": "pending"}
