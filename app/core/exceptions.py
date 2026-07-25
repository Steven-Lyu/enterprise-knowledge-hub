"""项目级异常和最小统一 HTTP 异常处理。"""

from collections.abc import Mapping
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """本项目业务异常的基类。"""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "APP_ERROR"

    def __init__(
        self,
        message: str,
        *,
        details: Mapping[str, Any] | None = None,
        request_id: str | None = None,
    ) -> None:
        self.message = message
        self.details = dict(details or {})
        self.request_id = request_id
        super().__init__(message)


class UnauthorizedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "UNAUTHORIZED"


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "NOT_FOUND"


class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "CONFLICT"


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """把项目内异常转换成已冻结的统一错误响应结构。"""

    request_id = exc.request_id or request.headers.get("X-Request-Id")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "request_id": request_id,
            "details": exc.details,
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """屏蔽内部异常细节，同时尽量保留 request_id 方便排查。"""

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_ERROR",
            "message": "internal server error",
            "request_id": request.headers.get("X-Request-Id"),
            "details": {},
        },
    )
