from models import DepartmentIn
from data.repositories import DepartmentRepository

# TODO:: Rework this functions into a single class


async def validate_department_creation_data(
    repository: DepartmentRepository, data: DepartmentIn
) -> None:
    if data.parent_id:
        await check_department_name_is_unique(repository, data)
        await check_parent_id_eq_new_department_id(repository, data)


async def check_department_name_is_unique(
    repository: DepartmentRepository, data: DepartmentIn
) -> None:
    parent_department = await repository.get_with_children(data.parent_id)
    if data.name in (dep.name for dep in parent_department.children):
        raise ValueError


async def check_parent_id_eq_new_department_id(
    repository: DepartmentRepository, data: DepartmentIn
) -> None:
    departments = await repository.get_all()

    if departments:
        last_department = departments[len(departments) - 1]
        new_department_id = last_department.id + 1
    else:
        new_department_id = 1

    if data.parent_id == new_department_id:
        raise ValueError
