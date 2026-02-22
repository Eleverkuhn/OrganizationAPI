from collections.abc import Sequence, Mapping
from typing import Generic, TypeVar, TypeAlias, override

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload, aliased
from sqlalchemy.sql import Select
from sqlalchemy.ext.asyncio import AsyncSession

from models import DepartmentGetData, DepartmentOut, EmployeeOut
from data.sql_models import Department, Employee

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

    async def _get_single(self, statement: Select) -> T | None:
        result = await self.session.execute(statement)
        entry = result.scalar_one_or_none()
        return entry


class DepartmentRepository(BaseRepository):
    model = Department

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @override
    async def create(self, data: DepartmentCreation) -> Department:
        department = await super().create(data)
        department = await self.get(department.id)
        return department

    async def get_recursively(
        self, id: int, depth: int, include_employees: bool
    ) -> Department | None:
        if include_employees:
            department = await self.get(id)
        else:
            department = await self.get_with_children(id)

        if not department:
            return

        if depth == 0:
            dumped_department = self._dump(department)
            employees = dumped_department.get("employees")
            if employees:
                employees = [EmployeeOut(**employee) for employee in employees]
                dumped_department["employees"] = employees
            department = DepartmentOut(**dumped_department)
            return department

        children = [
            await self.get_recursively(child.id, depth - 1, include_employees)
            for child in department.children
        ]

        department = DepartmentOut(**self._dump(department), children=children)

        return department

    async def get_with_children(self, id: int) -> Department | None:
        statement = (
            select(self.model)
            .options(selectinload(self.model.children))
            .where(self.model.id == id)
        )
        department = await self._get_single(statement)
        return department

    async def get(
        self, id: int
    ) -> Department | None:  # FIX: rename to 'get_with_employees'
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

    @staticmethod
    def _dump(department: Department) -> dict:
        result = {}
        for col in department.__table__.columns:
            key = col.name
            value = getattr(department, key)
            result[key] = value

        if department.employees:
            employees = [
                EmployeeRepository.dump(employee) for employee in department.employees
            ]
        else:
            employees = []
        result["employees"] = employees

        return result


class EmployeeRepository(BaseRepository):
    model = Employee

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id: int) -> Employee | None:
        statement = select(self.model).where(self.model.id == id)
        employee = await self._get_single(statement)
        return employee

    @staticmethod
    def dump(entry) -> dict:
        return {col.name: getattr(entry, col.name) for col in entry.__table__.columns}
