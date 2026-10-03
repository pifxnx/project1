from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from .config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.db_url)

sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db():
    async with sessionmaker() as session:
        yield session