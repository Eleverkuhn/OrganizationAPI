from datetime import datetime, date

from pydantic import BaseModel, Field, field_validator, model_validator

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


class DepartmentChange(DepartmentBase):
    name: str | None = Field(
        default=None,
        min_length=DefaultField.MIN_TITLE_LEN,
        max_length=DefaultField.MAX_TITLE_LEN,
    )


class DepartmentOut(DepartmentBase):
    id: int
    children: list["DepartmentOut"] | None = None
    employees: list["EmployeeOut"] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DepartmentGetData(BaseModel):
    id: int
    depth: int = Field(ge=1, le=DefaultField.MAX_DEPTH)
    include_employees: bool


class DepartmentDeleteData(BaseModel):
    id: int
    mode: str  # TODO:: add validation
    reassign_to_department_id: int | None = None  # TODO:: add validation

    @field_validator("mode", mode="after")
    @classmethod
    def mode_exists(cls, value: str) -> str:
        if value not in ("cascade", "reassign"):
            raise ValueError
        return value

    @model_validator(mode="after")
    def validate_reassign(self):
        if self.mode == "reassign" and self.reassign_to_department_id is None:
            raise ValueError
        return self


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
