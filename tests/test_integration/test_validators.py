import pytest

from models import DepartmentIn
from validators import (
    check_department_name_is_unique,
    check_parent_id_eq_new_department_id,
    check_new_parent_id_belongs_to_a_child,
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


@pytest.mark.parametrize("new_parent_id", (range(2, 6)))
@pytest.mark.asyncio
async def test_check_new_parent_id_belongs_to_a_child(
    department_repository: DepartmentRepository,
    departments_data: FixtureContent,
    new_parent_id: int,
) -> None:
    await department_repository.bulk_create(departments_data)
    with pytest.raises(ValueError):
        await check_new_parent_id_belongs_to_a_child(
            id=1, new_parent_id=new_parent_id, repository=department_repository
        )
