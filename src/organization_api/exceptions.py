from typing import NoReturn

from fastapi import HTTPException, status


class DepartmentDoesNotExist(BaseException): ...


def raise_unprocessable_content() -> NoReturn:
    msg = "Provide valid query params"
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=msg)
