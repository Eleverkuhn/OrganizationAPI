from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import DepartmentDoesNotExist
from models import (
    DepartmentIn,
    DepartmentOut,
    DepartmentChange,
    EmployeeIn,
    EmployeeOut,
)
from validators import (
    validate_department_get_query_data,
    validate_department_delete_query_data,
)
from services import (
    service_create_department,
    service_create_employee,
    service_get_department,
    service_change_department,
    service_delete_deparment,
)
from data.sql_models import Department, Employee
from data.db_connection import get_async_session

router = APIRouter(prefix="/departments")


@router.post(
    "/",
    name="create_department",
    status_code=status.HTTP_201_CREATED,
)
async def create_department(
    data: DepartmentIn,
    session: AsyncSession = Depends(get_async_session),
) -> DepartmentOut:
    try:
        department: Department = await service_create_department(data, session)
    except ValueError as exc:
        msg = str(exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    else:
        return department


@router.post(
    "/{id}/employees/", name="create_employee", status_code=status.HTTP_201_CREATED
)
async def create_employee(
    data: EmployeeIn, session: AsyncSession = Depends(get_async_session)
) -> EmployeeOut:
    try:
        employee: Employee = await service_create_employee(data, session)
    except IntegrityError:
        msg = "Can not create an employee for non existent department"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
    else:
        return employee


@router.get("/{id}", name="get_department", status_code=status.HTTP_200_OK)
async def get_department(
    id: int,
    depth: int = 1,
    include_employees: bool = True,
    session: AsyncSession = Depends(get_async_session),
) -> DepartmentOut:
    data = validate_department_get_query_data(id, depth, include_employees)
    try:
        department = await service_get_department(data, session)
    except DepartmentDoesNotExist as exc:
        msg = str(exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
    else:
        return department


@router.patch("/{id}", name="change_department", status_code=status.HTTP_200_OK)
async def change_department(
    id: int, data: DepartmentChange, session: AsyncSession = Depends(get_async_session)
) -> DepartmentOut:
    try:
        department = await service_change_department(id, data, session)
    except ValueError as exc:
        msg = str(exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    except DepartmentDoesNotExist as exc:
        msg = str(exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
    else:
        return department


@router.delete(
    "/{id}", name="delete_department", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_department(
    id: int,
    mode: str,
    reassign_to_department_id: int | None = None,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    data = validate_department_delete_query_data(id, mode, reassign_to_department_id)
    try:
        await service_delete_deparment(data, session)
    except ValidationError as exc:
        msg = str(exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    else:
        return
