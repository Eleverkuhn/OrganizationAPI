import asyncio
import json
from datetime import datetime, date
from pathlib import Path
from typing import TypeAlias, Sequence, Mapping

from sqlalchemy.ext.asyncio import AsyncSession

from config import BASE_DIR
from data.repositories import BaseRepository
from data.sql_models import Department, Employee
from data.db_connection import get_async_session

EmployeeData: TypeAlias = dict[str, int | str | date | None]

FIXTURE_DIR = BASE_DIR / "src" / "organization_api" / "data" / "fixtures"

FIXTURE_TO_MODEL = {"departments.json": Department, "employees.json": Employee}


async def main() -> None:
    session = await anext(get_async_session())
    # Имитация работы контекстного менеджера, т.к. я не могу обернуть get_async_session в декоратор из-за
    # @contextlib.contextmanager из-за того, что нужно будет использовать эту функцию как депенденси
    try:
        await seed_db(session)
    except:
        raise
    finally:
        await session.close()


async def seed_db(session: AsyncSession) -> None:
    for fixture_name, model in FIXTURE_TO_MODEL.items():
        data = get_data_from_fixture(fixture_name)
        check_date_fields(data)
        await BaseRepository(session, model).bulk_create(data)


def get_data_from_fixture(fixture_name: str) -> list[dict]:
    fixture_path = FIXTURE_DIR / fixture_name
    data = read_fixture(fixture_path)
    return data


def read_fixture(fixture: Path) -> list[dict]:
    # Маленький трейдоф. Лучше блокирующая функция, чем создавать ещё один синхронный движок для БД из-за одного скрипта
    with fixture.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def check_date_fields(data: Sequence[Mapping]) -> None:
    for entry in data:
        if entry.get("hired_at"):
            convert_str_to_date(entry)


def convert_str_to_date(entry: EmployeeData) -> None:
    entry["hired_at"] = datetime.strptime(entry["hired_at"], "%Y-%m-%d").date()


if __name__ == "__main__":
    asyncio.run(main())
