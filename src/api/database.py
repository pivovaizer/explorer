from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


from src.api.config import settings

engine = create_async_engine(settings.database_url, echo=(settings.app_env == "development"))
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

class DataBase(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


