import pytest
from unittest.mock import Mock
from sqlalchemy import select
from src.data.models.product import Product
from src.tasks.aggregation import aggregate_products_task


def test_aggregate_products(
    create_batch_sync,
    create_product_sync,
    patch_get_session,
    get_test_db_sync,
    monkeypatch,
):
    batch = create_batch_sync(1)
    create_product_sync("code1", batch.id)
    create_product_sync("code2", batch.id)
    create_product_sync("code3", batch.id)

    mock_webhook = Mock()
    monkeypatch.setattr(
        "src.tasks.aggregation.create_webhook_delivery_task",
        mock_webhook,
    )

    result = aggregate_products_task(batch.id, ["code1", "code2", "code3"])

    assert result == {
        "total": 3,
        "aggregated": 3,
        "failed": 0,
        "errors": [],
    }

    mock_webhook.delay.assert_called_once_with("product_aggregated", result)

    products = (
        get_test_db_sync.execute(select(Product).where(Product.batch_id == batch.id))
        .scalars()
        .all()
    )

    assert len(products) == 3
    assert all(p.is_aggregated for p in products)
