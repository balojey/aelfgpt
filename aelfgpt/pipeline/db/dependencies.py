from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import find_dotenv, dotenv_values


config = dotenv_values(find_dotenv())
db_url = config.get("DB_URL")
db_echo = config.get("DB_ECHO")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.

    :param request: current request.
    :yield: database session.
    """
    engine = create_async_engine(str(db_url), echo=bool(db_echo))
    session: AsyncSession = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    try:  # noqa: WPS501
        yield session
    finally:
        await session.commit()
        await session.close()


def get_engine():
    engine = create_engine(str(db_url), echo=bool(db_echo))
    return engine