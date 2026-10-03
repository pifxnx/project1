from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from ....core.exceptions import AppException


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


def register_exception_handler(app: FastAPI):
    app.add_exception_handler(AppException, app_exception_handler)
