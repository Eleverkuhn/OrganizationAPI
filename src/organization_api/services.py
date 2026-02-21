"""
В `services` обычно располагается бизнес логика, но т.к. тут её нет я решил использовать
его как промежуточный модуль между `web` и `data`, а также включить сюда логирование,
чтобы функции и методы в других модулях не разрастались
"""

from loguru import logger
from fastapi import Depends

from models import DepartmentIn
from validators import validate_department_creation_data
from data.repositories import DepartmentRepository
from data.sql_models import Department
from data.db_connection import get_async_session


async def service_create_department(
    data: DepartmentIn, session=Depends(get_async_session)
) -> Department:
    repository = DepartmentRepository(session)
    await validate_department_creation_data(repository, data)
    department = await repository.create(data.model_dump())

    logger.info(f"Created department '{department.name}' with ID `{department.id}")

    return department
