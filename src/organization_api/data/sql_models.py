from datetime import date, datetime

from sqlalchemy import (
    Integer,
    Date,
    DateTime,
    String,
    CheckConstraint,
    ForeignKey,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    attributes,
)
from sqlalchemy.ext.asyncio import AsyncAttrs


class DefaultField:
    MIN_TITLE_LEN = 1
    MAX_TITLE_LEN = 200
    MAX_DEPTH = 5


class Base(AsyncAttrs, DeclarativeBase):
    pass


class BaseMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Department(BaseMixin, Base):
    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(
        String(DefaultField.MAX_TITLE_LEN), nullable=False
    )
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=True
    )

    parent: Mapped["Department"] = relationship(
        "Department", remote_side="Department.id", back_populates="children"
    )
    children: Mapped[list["Department"]] = relationship(
        "Department",
        back_populates="parent",
        lazy="selectin",
        cascade="all, delete",
        passive_deletes=True,
    )
    employees: Mapped[list["Employee"]] = relationship(
        "Employee",
        back_populates="department",
        lazy="selectin",
        join_depth=DefaultField.MAX_DEPTH,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            f"char_length(name) >= {DefaultField.MIN_TITLE_LEN} AND char_length(name) <= {DefaultField.MAX_TITLE_LEN}",
            name="name_length_check",
        ),
    )

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name} parent_id={self.parent_id}>"


class Employee(BaseMixin, Base):
    __tablename__ = "employees"

    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(DefaultField.MAX_TITLE_LEN), nullable=False
    )
    position: Mapped[str] = mapped_column(
        String(DefaultField.MAX_TITLE_LEN), nullable=False
    )
    hired_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    department: Mapped["Department"] = relationship(
        "Department", back_populates="employees"
    )

    __table_args__ = (
        CheckConstraint(
            f"char_length(full_name) >= {DefaultField.MIN_TITLE_LEN} AND char_length(full_name) <= {DefaultField.MAX_TITLE_LEN}",
            name="full_name_length_check",
        ),
        CheckConstraint(
            f"char_length(position) >= {DefaultField.MIN_TITLE_LEN} AND char_length(position) <= {DefaultField.MAX_TITLE_LEN}",
            name="position_length_check",
        ),
    )
