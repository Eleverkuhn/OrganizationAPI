import pytest
import pytest_asyncio
from loguru import logger
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from data.repositories import DepartmentRepository


@pytest.mark.asyncio
async def test_create_department(client: AsyncClient, session: AsyncSession) -> None:
    data = {"name": "test_department"}
    response = await client.post(app.url_path_for("create_department"), json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    logger.debug(result)
    department = await DepartmentRepository(session).get(result.get("id"))
    assert department
