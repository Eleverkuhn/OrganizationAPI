"""
В `services` обычно располагается бизнес логика, но т.к. тут её нет я решил использовать
его как промежуточный модуль между `web` и `data`, а также включить сюда логирование,
чтобы функции и методы в других модулях не разрастались
"""

from loguru import logger
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models import (
    DepartmentIn,
    DepartmentOut,
    DepartmentChange,
    EmployeeIn,
    EmployeeOut,
    DepartmentGetData,
    DepartmentDeleteData,
)
from validators import (
    validate_department_creation_data,
    validate_department_change_data,
    check_department_exists,
)
from data.repositories import DepartmentRepository, EmployeeRepository
from data.sql_models import Department, Employee
from data.db_connection import get_async_session


class RecursiveDepartmentLoader:
    """
    Я решил вынести рекурсивное получение подразделений из DepartmentRepository в отдельный класс, т.к. для рекурсивного
    обхода требуется слишком много разных задач: обращения к бд, сериализация, проверки. Плюс здесь происходит оркестрация
    двух разных репозиториев, и лучше вынести её на верхний уровень, а не давать одному репозиторию вызывать другой
    """

    def __init__(
        self,
        include_employees: bool,
        session: AsyncSession = Depends(get_async_session),
    ) -> None:
        self.include_employees = include_employees
        self.department_repository = DepartmentRepository(session)

    async def exec(self, id: int, depth: int) -> DepartmentOut | None:
        department = await self._get_department(id)

        if not department:
            return

        if depth == 0:
            return self._serialize_child(department)

        children = await self._get_children(depth, department)  # Вызов рекурсии

        result = self._serialize_result(department, children)

        return result

    async def _get_department(self, id) -> Department | None:
        if self.include_employees:
            department = await self.department_repository.get_with_employees(id)
        else:
            department = await self.department_repository.get_with_children(id)
        return department

    def _serialize_child(self, department: Department) -> DepartmentOut:
        department_dumped = self.department_repository.dump(department)

        employees_serialized = self._serialize_employees(department.employees)

        department_serialized = DepartmentOut(
            **department_dumped, employees=employees_serialized
        )
        return department_serialized

    def _serialize_employees(
        self, employees: list[Employee] | None
    ) -> list[EmployeeOut] | None:
        if employees:
            serialized = [
                EmployeeOut(**EmployeeRepository.dump(employee))
                for employee in employees
            ]
        else:
            serialized = []
        return serialized

    async def _get_children(
        self, depth: int, department: Department
    ) -> list[DepartmentOut]:
        children = [
            await self.exec(child.id, depth - 1) for child in department.children
        ]
        return children

    def _serialize_result(
        self, department: Department, children: list[DepartmentOut] | None
    ) -> DepartmentOut:
        department_dumped = self.department_repository.dump(department)
        employees_serialized = self._serialize_employees((department.employees))
        department_serialized = DepartmentOut(
            **department_dumped, children=children, employees=employees_serialized
        )
        return department_serialized


async def service_create_department(
    data: DepartmentIn, session=Depends(get_async_session)
) -> Department:
    repository = DepartmentRepository(session)
    await validate_department_creation_data(repository, data)
    department = await repository.create(data.model_dump())

    logger.info(f"Created department '{department.name}' with ID `{department.id}")

    return department


async def service_create_employee(
    data: EmployeeIn, session=Depends(get_async_session)
) -> Employee:
    repository = EmployeeRepository(session)
    employee = await repository.create(data.model_dump())
    logger.debug(employee)

    logger.info(f"Created employee {employee.full_name} with ID {employee.id}")

    return employee


async def service_get_department(
    data: DepartmentGetData, session: AsyncSession
) -> DepartmentOut | None:
    loader = RecursiveDepartmentLoader(data.include_employees, session)
    department = await loader.exec(data.id, data.depth)
    return department


async def service_change_department(
    id: int, data: DepartmentChange, session: AsyncSession
) -> dict | None:
    repository = DepartmentRepository(session)
    await validate_department_change_data(id, data, repository)

    department = await repository.change(id, data.model_dump())
    department_dumped = repository.dump(department)

    return department_dumped


async def service_delete_deparment(
    data: DepartmentDeleteData, session: AsyncSession
) -> None:
    repository = DepartmentRepository(session)
    await check_department_exists(data.id, repository)

    if data.mode == "cascade":
        await repository.cascade_delete(data.id)
        logger.info(f"Casacde delition of a department with ID: {data.id}")

    else:  # Всего два метода удаления
        await check_department_exists(data.reassign_to_department_id, repository)
        await repository.reassign_delete(data.id, data.reassign_to_department_id)
        logger.info(f"Reassign delete of a deparment with ID: {data.id}")
