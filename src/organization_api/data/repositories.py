from collections.abc import Sequence, Mapping
from typing import Generic, TypeVar, TypeAlias, override

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from sqlalchemy.ext.asyncio import AsyncSession

from data.sql_models import Department, Employee

T = TypeVar("T")
DepartmentCreation: TypeAlias = Mapping[str, str | int]


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self.session = session
        self.model = model

    async def get(self, id: int) -> T | None:
        statement = select(self.model).where(self.model.id == id)
        entry = await self._get_single(statement)
        return entry

    async def get_all(self) -> list[T]:
        entries = await self.session.execute(select(self.model))
        result = list(entries.scalars().all())
        return result

    async def bulk_create(self, data: Sequence[Mapping]) -> None:
        for entry in data:
            await self.create(entry)

    async def create(self, data: Mapping) -> T:
        entry = self.model(**data)
        await self._add(entry)
        return entry

    async def _add(self, entry: T) -> None:
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)

    async def _get_single(self, statement: Select) -> T | None:
        result = await self.session.execute(statement)
        entry = result.scalar_one_or_none()
        return entry

    @staticmethod
    def dump(entry) -> dict:
        return {col.name: getattr(entry, col.name) for col in entry.__table__.columns}


class DepartmentRepository(BaseRepository):
    model = Department

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @override
    async def create(self, data: DepartmentCreation) -> Department | None:
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

    async def get_with_employees(self, id: int) -> Department | None:
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

    async def change(self, id: int, data: DepartmentCreation) -> Department | None:
        department = await self.get(id)
        if department:
            await self._update(department, data)
        return department

    async def _update(self, department: Department, data: DepartmentCreation) -> None:
        for field, value in data.items():
            if hasattr(department, field) and value:
                setattr(department, field, value)
        await self._add(department)

    async def _get_new_department_id(self) -> int:
        """Используется в validators.validate_department_creation_data. Вычисляет значения следующего созданного ID"""
        departments = await self.get_all()
        if departments:
            last_department = departments[len(departments) - 1]
            new_department_id = last_department.id + 1
        else:
            new_department_id = 1
        return new_department_id


class EmployeeRepository(BaseRepository):
    model = Employee

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
