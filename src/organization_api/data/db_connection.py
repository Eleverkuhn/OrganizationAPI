from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from config import env

DB_URL = (
    f"postgresql+asyncpg://{env.postgres_user}:"
    f"{env.postgres_password}"
    f"@{env.postgres_host}:{env.postgres_port}/{env.postgres_db}"
)

engine = create_async_engine(DB_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
