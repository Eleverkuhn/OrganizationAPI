import json
from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from config import BASE_DIR
from data.repositories import BaseRepository
from data.sql_models import Department, Employee

FIXTURE_DIR = BASE_DIR / "src" / "organization_api" / "data" / "fixtures"

FIXTURE_TO_MODEL = {"departments.json": Department, "employees.json": Employee}


async def seed_db(session: AsyncSession) -> None:
    # FIX: Refactor this
    for fixture_name, model in FIXTURE_TO_MODEL.items():
        fixture_path = FIXTURE_DIR / fixture_name
        data = read_fixture(fixture_path)
        for entry in data:
            if entry.get("hired_at"):
                entry["hired_at"] = datetime.strptime(
                    entry["hired_at"], "%Y-%m-%d"
                ).date()
        await BaseRepository(session, model).bulk_create(data)


def read_fixture(fixture: Path) -> list[dict]:
    with fixture.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data
