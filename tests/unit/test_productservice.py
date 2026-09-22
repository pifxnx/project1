import pytest
from sqlalchemy.exc import IntegrityError
from unittest.mock import AsyncMock
from src.domain.services.product_service import ProductService
from src.api.v1.schemas.product import ProductCreate
from src.data.models.product import Product
from src.domain.exceptions.product_exception import (
    ProductAlreadyExistsException,
    ProductNotFoundException,
)


@pytest.mark.asyncio
async def test_product_service_create():
    repo = AsyncMock()
    repo.create.return_value = Product(
        id=1, unique_code="code1", batch_id=1, is_aggregated=False
    )

    service = ProductService(repo)

    product = await service.create(ProductCreate(unique_code="code1", batch_id=1))
    repo.create.assert_awaited_once()

    assert product.id == 1
    assert product.unique_code == "code1"


@pytest.mark.asyncio
async def test_product_service_create_already_exists():
    repo = AsyncMock()
    repo.create.side_effect = IntegrityError(
        "duplicate key value violates unique constraint", params=None, orig=None
    )

    service = ProductService(repo)

    with pytest.raises(ProductAlreadyExistsException):
        await service.create(ProductCreate(unique_code="code1", batch_id=1))

    repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_product_service_get_by_id():
    repo = AsyncMock()
    repo.get_by_id.return_value = Product(
        id=1, unique_code="code1", batch_id=1, is_aggregated=False
    )

    service = ProductService(repo)

    product = await service.get_by_id(1)
    repo.get_by_id.assert_awaited_once_with(1)

    assert product.id == 1
    assert product.unique_code == "code1"
    assert product.is_aggregated == False


@pytest.mark.asyncio
async def test_product_service_get_by_id_not_found():
    repo = AsyncMock()

    repo.get_by_id.return_value = None
    service = ProductService(repo)

    with pytest.raises(ProductNotFoundException):
        await service.get_by_id(product_id=1)

    repo.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_product_service_get_by_batch_id():
    repo = AsyncMock()

    repo.get_by_batch_id.return_value = [
        Product(unique_code="code22", batch_id=1, is_aggregated=False),
        Product(unique_code="code23", batch_id=1, is_aggregated=False),
    ]
    service = ProductService(repo)

    products = await service.get_by_batch_id(1)

    assert len(products) == 2
    assert {p.unique_code for p in products} == {"code22", "code23"}


@pytest.mark.asyncio
async def test_product_service_get_by_batch_id_no_products():
    repo = AsyncMock()

    repo.get_by_batch_id.return_value = []

    service = ProductService(repo)

    products = await service.get_by_batch_id(1)

    assert len(products) == 0
