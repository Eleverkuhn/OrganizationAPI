from loguru import logger
from fastapi import APIRouter, Depends, status

from models import DepartmentIn, DepartmentOut
from services import service_create_department
from data.sql_models import Department

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
    data: DepartmentIn, department: Department = Depends(service_create_department)
) -> DepartmentOut:
    return department
