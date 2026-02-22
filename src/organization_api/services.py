"""
В `services` обычно располагается бизнес логика, но т.к. тут её нет я решил использовать
его как промежуточный модуль между `web` и `data`, а также включить сюда логирование,
чтобы функции и методы в других модулях не разрастались
"""

from loguru import logger
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models import DepartmentIn, DepartmentOut, EmployeeIn, DepartmentGetData
from validators import validate_department_creation_data
from data.repositories import DepartmentRepository, EmployeeRepository
from data.sql_models import Department, Employee
from data.db_connection import get_async_session


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
) -> Department | None:
    repository = DepartmentRepository(session)
    department = await repository.get_recursively(**data.model_dump())
    return department
