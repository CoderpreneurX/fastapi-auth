from fastapi import FastAPI

from fastapi_auth.core.handlers import (
    validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError


def setup_auth(app: FastAPI) -> None:
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
