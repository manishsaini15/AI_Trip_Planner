from fastapi import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


class AppException(Exception):
    def __init__(self, message: str, status_code: int = HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(message)
        self.status_code = status_code


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": str(exc),
            "detail": "An application error occurred.",
        },
    )
