from models import DepartmentIn


def test_strip_name_field() -> None:
    data = {"name": "   whites spaces             "}
    department = DepartmentIn(**data)
    assert not department.name == data["name"]
