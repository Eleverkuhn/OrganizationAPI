from os import stat
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import DepartmentIn, DepartmentOut, EmployeeIn, EmployeeOut
from services import service_create_department, service_create_employee
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
