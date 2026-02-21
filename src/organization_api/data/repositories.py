from collections.abc import Sequence, Mapping
from typing import Any, Generic, TypeVar, TypeAlias, override

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from sqlalchemy.ext.asyncio import AsyncSession

from data.sql_models import Base, Department, Employee

T = TypeVar("T")
DepartmentCreation: TypeAlias = Mapping[str, str | int]


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        self.model = model

    async def get_all(self) -> list[T]:
        entries = await self.session.execute(select(self.model))
        result = list(entries.scalars().all())
        return result

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


class DepartmentRepository(BaseRepository):
    model = Department

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @override
    async def create(self, data: DepartmentCreation) -> Department:
        department = await super().create(data)
        department = await self.get(department.id)
        return department

    async def get_with_children(self, id: int) -> Department | None:
        statement = (
            select(self.model)
            .options(selectinload(self.model.children))
            .where(self.model.id == id)
        )
        department = await self._get_single(statement)
        return department

    async def get(self, id: int) -> Department | None:
        statement = (
            select(self.model)
            .options(
                selectinload(self.model.employees),
                selectinload(self.model.children),
            )
            .where(self.model.id == id)
        )
        department = await self._get_single(statement)
        return department

    async def _get_single(self, statement: Select) -> Department | None:
        result = await self.session.execute(statement)
        department = result.scalar_one_or_none()
        return department


class EmployeeRepository(BaseRepository):
    model = Employee

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
