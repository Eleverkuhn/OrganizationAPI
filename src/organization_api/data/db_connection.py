from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import env

DB_URL = (
    f"postgresql+asyncpg://{env.postgres_user}:"
    f"{env.postgres_password}"
    f"@{env.postgres_host}:{env.postgres_port}/{env.postgres_db}"
)

DB_SYNC_URL = (
    f"postgresql+psycopg://{env.postgres_user}:"
    f"{env.postgres_password}"
    f"@{env.postgres_host}:{env.postgres_port}/{env.postgres_db}"
)

engine = create_async_engine(DB_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
