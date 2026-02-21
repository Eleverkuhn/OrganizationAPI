from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV = BASE_DIR / ".env"


class Env(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: str

    postgres_test_db: str
    postgres_test_host: str
    postgres_test_port: str

    fastapi_host: str
    fastapi_port: str

    pythonpath: str

    model_config = SettingsConfigDict(env_file=ENV)


env = Env()
