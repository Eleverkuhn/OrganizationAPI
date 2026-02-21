from datetime import datetime, date

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
    department_id: int
    full_name: str = Field(
        min_length=DefaultField.MIN_TITLE_LEN, max_length=DefaultField.MAX_TITLE_LEN
    )
    position: str = Field(
        min_length=DefaultField.MIN_TITLE_LEN, max_length=DefaultField.MAX_TITLE_LEN
    )
    hired_at: date | None = None


class EmployeeIn(EmployeeBase):
    pass


class EmployeeOut(EmployeeBase):
    id: int
    created_at: datetime
