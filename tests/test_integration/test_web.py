import pytest
from loguru import logger
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from data.seed_db import check_date_fields
from data.repositories import DepartmentRepository, EmployeeRepository
from data.sql_models import Department
from tests.conftest import FixtureContent


@pytest.mark.asyncio
async def test_create_department(client: AsyncClient, session: AsyncSession) -> None:
    data = {"name": "test_department"}
    response = await client.post(app.url_path_for("create_department"), json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    department = await DepartmentRepository(session).get(result.get("id"))
    assert department


@pytest.mark.asyncio
async def test_create_department_returns_400_if_name_is_not_unqiue(
    client: AsyncClient,
    departments_data: FixtureContent,
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


@pytest.mark.parametrize("departments_data", [1], indirect=True)
@pytest.mark.asyncio
async def test_create_employee(
    client: AsyncClient, session: AsyncSession, created_departments: list[Department]
) -> None:
    department = created_departments[0]
    data = {
        "department_id": department.id,
        "full_name": "Test Employee",
        "position": "Test position",
        "hired_at": "2026-02-21",
    }
    response = await client.post(
        app.url_path_for("create_employee", id=department.id), json=data
    )
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    employee = await EmployeeRepository(session).get(result.get("id"))
    assert employee


@pytest.mark.parametrize("employees_data", [1], indirect=True)
@pytest.mark.asyncio
async def test_create_employee_returns_404_for_non_existent_department(
    client: AsyncClient, employees_data: FixtureContent
) -> None:
    employee = employees_data[0]
    employee.pop("id")
    response = await client.post(
        app.url_path_for("create_employee", id=employee["department_id"]), json=employee
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_department(
    client: AsyncClient,
    departments_data: FixtureContent,
    employees_data: FixtureContent,
    department_repository: DepartmentRepository,
    employee_repository: EmployeeRepository,
) -> None:
    await department_repository.bulk_create(departments_data)
    check_date_fields(employees_data)
    await employee_repository.bulk_create(employees_data)

    params = {"depth": 1}

    response = await client.get(app.url_path_for("get_department", id=1), params=params)
    assert response.status_code == status.HTTP_200_OK

    content = response.json()
    assert content


@pytest.mark.asyncio
async def test_get_department_raises_404_if_does_not_exist(client: AsyncClient) -> None:
    params = {"depth": 1}
    response = await client.get(app.url_path_for("get_department", id=1), params=params)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("depth", [0, 6])
@pytest.mark.asyncio
async def test_get_department_does_not_allow_to_set_invalid_recursion_depth(
    client: AsyncClient, depth: int
) -> None:
    params = {"depth": depth}
    response = await client.get(app.url_path_for("get_department", id=1), params=params)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
