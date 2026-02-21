from collections.abc import AsyncGenerator
from typing import Callable, TypeAlias
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from main import app
from config import env
from data.seed_db import FIXTURE_DIR, read_fixture
from data.repositories import DepartmentRepository
from data.sql_models import Base
from data.db_connection import get_async_session

DepartmentData: TypeAlias = list[dict[str, str | int | None]]

TEST_DB_URL = (
    f"postgresql+asyncpg://{env.postgres_user}:"
    f"{env.postgres_password}"
    f"@{env.postgres_test_host}:{env.postgres_test_port}/{env.postgres_test_db}"
)

engine = create_async_engine(
    TEST_DB_URL, echo=True
)  # Здесь приходится копипастить, т.к. даже если сделать функцию,
# геренирующую engine, то её нельзя будет применить к "прод" ДБ
# из-за того, что создание сессии через async_sesion_maker будет
# каждый раз создавать ноый engine
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def create_tables() -> AsyncGenerator:
    await run_sync(engine, Base.metadata.create_all)
    yield
    await run_sync(engine, Base.metadata.drop_all)
    await engine.dispose()


async def run_sync(engine: AsyncEngine, cmd: Callable) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(cmd)


@pytest_asyncio.fixture
async def session(create_tables: AsyncGenerator) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@pytest.fixture(autouse=True)
def override_session(session):
    async def override():
        yield session

    app.dependency_overrides[get_async_session] = override
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def departments_fixture() -> Path:
    return FIXTURE_DIR / "departments.json"


@pytest.fixture
def departments_data(departments_fixture) -> DepartmentData:
    return read_fixture(departments_fixture)


@pytest.fixture
def department_repository(session: AsyncSession) -> DepartmentRepository:
    return DepartmentRepository(session)
