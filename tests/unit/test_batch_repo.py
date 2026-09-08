from sqlalchemy import select
import pytest


@pytest.mark.asyncio
async def test_connection(get_test_db):
    result = await get_test_db.execute(select(1))

    assert result.scalar_one() == 1