import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from services import RecursiveDepartmentLoader
from data.seed_db import check_date_fields
from data.repositories import DepartmentRepository, EmployeeRepository
from tests.conftest import FixtureContent


@pytest.mark.asyncio
async def test_recursive_department_loader(
    session: AsyncSession,
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

    department = await RecursiveDepartmentLoader(True, session).exec(1, 3)

    assert department
