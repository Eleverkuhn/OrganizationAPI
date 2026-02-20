import json
from collections.abc import Sequence, Mapping
from pathlib import Path
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from data.sql_models import Department, Employee

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        self.model = model

    async def bulk_create(self, data: Sequence[Mapping]) -> None:
        for entry in data:
            await self.create(entry)

    async def create(self, data: Mapping) -> T:
        entry = self.model(**data)
        self.session.add(entry)
        await self._refresh(entry)
        return entry

    async def _refresh(self, entry: T) -> None:
        await self.session.commit()
        await self.session.refresh(entry)
