from collections.abc import Sequence, Mapping
from typing import Any, Generic, TypeVar, override

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from data.sql_models import Base, Department, Employee

T = TypeVar("T")


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

    @staticmethod
    def dump(entry: Base) -> dict[str, Any]:
        return {col.name: getattr(entry, col.name) for col in entry.__table__.columns}


class DepartmentRepository(BaseRepository):
    model = Department

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @override
    async def create(self, data: Mapping) -> Department:
        department = await super().create(data)
        department = await self.get(department.id)
        return department

    async def get(self, id: int) -> Department | None:
        statement = (
            select(self.model)
            .options(
                selectinload(Department.employees),
                selectinload(Department.children),
            )
            .where(Department.id == id)
        )
        result = await self.session.execute(statement)
        department = result.scalar_one()
        return department


class EmployeeRepository(BaseRepository):
    model = Employee

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
