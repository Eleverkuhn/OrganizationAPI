from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models import DepartmentIn, DepartmentOut
from services import service_create_department
from data.sql_models import Department
from data.db_connection import get_async_session

router = APIRouter()


@router.get("/")
async def main():
    # FIX: remove this
    logger.debug("test in console")
    logger.info("test in file")
    return {"Hello": "world"}


@router.post(
    "/departments", name="create_department", status_code=status.HTTP_201_CREATED
)
async def create_department(
    data: DepartmentIn,
    session: AsyncSession = Depends(get_async_session),
) -> DepartmentOut:
    try:
        response = await service_create_department(data, session)
    except ValueError as exc:
        msg = str(exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    else:
        return response
