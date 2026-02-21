import pytest
from loguru import logger
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from data.repositories import DepartmentRepository
from tests.conftest import DepartmentData


@pytest.mark.asyncio
async def test_create_department(client: AsyncClient, session: AsyncSession) -> None:
    data = {"name": "test_department"}
    response = await client.post(app.url_path_for("create_department"), json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    logger.debug(result)
    department = await DepartmentRepository(session).get(result.get("id"))
    assert department


@pytest.mark.asyncio
async def test_create_department_returns_400_if_name_is_not_unqiue(
    client: AsyncClient,
    departments_data: DepartmentData,
    department_repository: DepartmentRepository,
) -> None:
    for entry in departments_data[:2]:
        await department_repository.create(entry)
    data = {"name": "Operations", "parent_id": 1}

    response = await client.post(app.url_path_for("create_department"), json=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_create_department_returns_400_if_parent_id_eq_new_department_id(
    client: AsyncClient,
) -> None:
    data = {"name": "test_department", "parent_id": 1}
    response = await client.post(app.url_path_for("create_department"), json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
