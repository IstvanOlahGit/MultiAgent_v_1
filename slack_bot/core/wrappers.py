from functools import wraps
from typing import Generic, Optional, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse


T = TypeVar('T')


class ErrorSlackResponse(BaseModel):
    message: str


class SlackResponseWrapper(BaseModel, Generic[T]):
    data: Optional[T] = None
    successful: bool = True
    error: Optional[ErrorSlackResponse] = None

    def response(self, status_code: int):
        return JSONResponse(
            status_code=status_code,
            content={
                "data": self.data,
                "successful": self.successful,
                "error": self.error.dict() if self.error else None
            }
        )


def exception_wrapper(http_error: int, error_message: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise HTTPException(status_code=http_error, detail=error_message) from e

        return wrapper

    return decorator







