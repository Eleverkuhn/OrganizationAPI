import pytest

from models import DepartmentIn
from validators import (
    check_department_name_is_unique,
    check_parent_id_eq_new_department_id,
)
from data.repositories import DepartmentRepository
from tests.conftest import FixtureContent


@pytest.mark.asyncio
async def test_check_name_is_unique_raises_value_error(
    department_repository: DepartmentRepository, departments_data: FixtureContent
) -> None:
    _, existing_department = data = departments_data[:2]
    for entry in data:
        await department_repository.create(entry)

    data = DepartmentIn(**existing_department)
    with pytest.raises(ValueError):
        await check_department_name_is_unique(department_repository, data)


@pytest.mark.asyncio
async def test_check_parent_id_eq_new_department_id(
    department_repository: DepartmentRepository,
) -> None:
    data = {"name": "test_dep", "parent_id": 1}
    data = DepartmentIn(**data)
    with pytest.raises(ValueError):
        await check_parent_id_eq_new_department_id(department_repository, data)
