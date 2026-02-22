from loguru import logger

from exceptions import DepartmentDoesNotExist
from models import DepartmentIn, DepartmentChange
from data.repositories import DepartmentRepository

# TODO: Rework this functions into a single class


async def validate_department_change_data(
    id: int, data: DepartmentChange, repository: DepartmentRepository
) -> None:
    await check_department_exists(id, repository)
    if data.parent_id:
        await check_department_exists(data.parent_id, repository)
        check_ids_are_eq(id, data.parent_id)
        await check_new_parent_id_belongs_to_a_child(id, data.parent_id, repository)


async def check_department_exists(id: int, repository: DepartmentRepository) -> None:
    logger.debug("inside func")
    department = await repository.get(id)
    if not department:
        raise DepartmentDoesNotExist(f"Department with id {id} does not exist")


async def check_new_parent_id_belongs_to_a_child(
    id: int, new_parent_id: int, repository: DepartmentRepository
) -> None:
    department = await repository.get_with_children(id)

    for child in department.children:
        if new_parent_id == child.id:
            raise ValueError("Department can not be a parent to itself")
        await check_new_parent_id_belongs_to_a_child(
            child.id, new_parent_id, repository
        )


async def validate_department_creation_data(
    repository: DepartmentRepository, data: DepartmentIn
) -> None:
    if data.parent_id:
        await check_parent_id_eq_new_department_id(repository, data)
        await check_department_name_is_unique(repository, data)


async def check_department_name_is_unique(
    repository: DepartmentRepository, data: DepartmentIn
) -> None:
    parent_department = await repository.get_with_children(data.parent_id)
    if data.name in (dep.name for dep in parent_department.children):
        raise ValueError(
            "Department-child name should be unique for a single department-parent"
        )


async def check_parent_id_eq_new_department_id(
    repository: DepartmentRepository, data: DepartmentIn
) -> None:
    new_department_id = await repository._get_new_department_id()
    check_ids_are_eq(new_department_id, data.parent_id)


def check_ids_are_eq(first: int, second: int) -> None:
    if first == second:
        raise ValueError("Department cannot be a parent to itself")
