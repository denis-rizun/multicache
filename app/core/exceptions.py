import structlog
from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = structlog.get_logger()


class AppError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    def __init__(self, detail: str = "Not found") -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail)


def register_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(exc.detail, status_code=exc.status_code, path=request.url.path, method=request.method)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
