from models import DepartmentIn
from data.repositories import DepartmentRepository


async def validate_department_creation_data(
    repository: DepartmentRepository, data: DepartmentIn
) -> None:
    if data.parent_id:
        await check_department_name_is_unique(repository, data)


async def check_department_name_is_unique(
    repository: DepartmentRepository, data: DepartmentIn
) -> None:
    parent_department = await repository.get_with_children(data.parent_id)
    if data.name in (dep.name for dep in parent_department.children):
        raise ValueError
