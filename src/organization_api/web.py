from loguru import logger
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def main():
    logger.debug("test in console")
    logger.info("test in file")
    return {"Hello": "world"}
