import json

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.seed_db import FIXTURE_DIR, read_fixture
from data.repositories import BaseRepository
from data.sql_models import Department


@pytest.mark.asyncio
async def test_bulk_create(session: AsyncSession) -> None:
    repository = BaseRepository(session, Department)
    fixture = FIXTURE_DIR / "departments.json"
    data = read_fixture(fixture)

    await repository.bulk_create(data)

    created = await session.execute(select(Department))
    departments = created.scalars().all()

    assert len(departments) == len(data)
