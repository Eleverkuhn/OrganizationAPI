from fastapi import FastAPI

from logger_config import setup_logger
from web import router

setup_logger()

app = FastAPI()

app.include_router(router)
