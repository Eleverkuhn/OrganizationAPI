import json
from pathlib import Path

from config import BASE_DIR

FIXTURE_DIR = BASE_DIR / "src" / "organization_api" / "data" / "fixtures"


def read_fixture(fixture: Path) -> list[dict]:
    with fixture.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data
