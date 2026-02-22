import pytest
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from models import DepartmentGetData
from data.seed_db import FIXTURE_DIR, read_fixture, seed_db, check_date_fields
from data.repositories import BaseRepository, DepartmentRepository, EmployeeRepository
from data.sql_models import Department
from tests.conftest import FixtureContent


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


@pytest.mark.asyncio
async def test_get_recursively(
    department_repository: DepartmentRepository,
    employee_repository: EmployeeRepository,
    departments_data: FixtureContent,
    employees_data: FixtureContent,
) -> None:
    await department_repository.bulk_create(departments_data)
    check_date_fields(
        employees_data
    )  # FIX: move this check to `employees_data` fixture
    await employee_repository.bulk_create(employees_data)

    data = DepartmentGetData(id=1, depth=3, include_employees=True)
    department = await department_repository.get_recursively(
        data.id, data.depth, data.include_employees
    )

    logger.debug(f"Root dep: {department}")
    logger.debug(f"1st level children: {department.children}")

    for child in department.children:
        logger.debug(f"2nd level children: {child.children}")
        for another_child in child.children:
            logger.debug(f"3rd level children: {another_child.children}")

    logger.debug(f"Employees: {department.employees}")
