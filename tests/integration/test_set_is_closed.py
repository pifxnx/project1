import pytest_asyncio
import pytest
from src.domain.exceptions.batch_exception import BatchNotFoundException
from src.domain.services.batch_service import BatchService
from src.data.repositories.batch_repository import BatchRepository



@pytest.mark.asyncio
async def test_is_closed_not_found(get_test_db):
    repository = BatchRepository(get_test_db)
    service = BatchService(repository)
    with pytest.raises(BatchNotFoundException):
        await service.set_is_closed(9876)


@pytest.mark.asyncio
async def test_is_closed_on_and_off(get_test_db, create_batch):
    service = BatchService(BatchRepository(get_test_db))
    await service.set_is_closed(create_batch.id)

    batch = await service.get_by_id(create_batch.id)
    assert batch.is_closed == True
