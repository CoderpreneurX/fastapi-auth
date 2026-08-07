from collections import defaultdict

from fastapi import Request
from fastapi.exceptions import RequestValidationError

from .responses import ValidationErrorResponse


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> ValidationErrorResponse:
    errors: defaultdict[str, list[str]] = defaultdict(list)

    for error in exc.errors():
        loc = error.get("loc", ())
        message = error.get("msg", "Invalid input.")

        # Drop the source ("body", "query", "path", "header", "cookie")
        field_path = [str(part) for part in loc[1:]]

        # Root-level validation errors
        field = ".".join(field_path) if field_path else "__root__"

        errors[field].append(message)

    return ValidationErrorResponse(errors=dict(errors))
