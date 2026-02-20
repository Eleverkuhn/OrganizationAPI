from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from data.sql_models import DefaultField


class DepartmentBase(BaseModel):
    # Создаю базовый класс, чтобы иерархия наследования была более очевидной
    name: str = Field(
        min_length=DefaultField.MIN_TITLE_LEN, max_length=DefaultField.MAX_TITLE_LEN
    )
    parent_id: int | None = None

    @field_validator("name", mode="after")
    @classmethod
    def strip(cls, value: str) -> str:
        return value.strip()


class DepartmentIn(DepartmentBase):
    pass


class DepartmentOut(DepartmentBase):
    id: int
    children: list["DepartmentOut"] | None = None
    employees: list["EmployeeOut"] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EmployeeBase(BaseModel):
    pass


class EmployeeOut(EmployeeBase):
    pass
