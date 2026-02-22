import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from data.seed_db import FIXTURE_DIR, read_fixture, seed_db, check_date_fields
from data.repositories import BaseRepository, DepartmentRepository, EmployeeRepository
from data.sql_models import Department


@pytest.mark.asyncio
async def test_bulk_create(
    session: AsyncSession,
) -> None:
    repository = BaseRepository(session, Department)
    fixture = FIXTURE_DIR / "departments.json"
    data = read_fixture(fixture)

    await repository.bulk_create(data)

    departments = await repository.get_all()

    assert len(departments) == len(data)


@pytest.mark.asyncio
async def test_seed_db(session: AsyncSession) -> None:
    await seed_db(session)

    departments = await DepartmentRepository(session).get_all()
    employees = await EmployeeRepository(session).get_all()
    departments_data = read_fixture(FIXTURE_DIR / "departments.json")
    employees_data = read_fixture(FIXTURE_DIR / "employees.json")

    assert len(departments) == len(departments_data)
    assert len(employees) == len(employees_data)
