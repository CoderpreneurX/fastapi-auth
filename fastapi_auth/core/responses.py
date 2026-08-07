from typing import Any

from fastapi.responses import JSONResponse


class APIResponse(JSONResponse):
    def __init__(
        self,
        data: dict[str, Any] | list[dict[str, Any]],
        message: str = "",
        status_code: int = 200,
    ) -> None:
        super().__init__(
            status_code=status_code,
            content={
                "success": True,
                "data": data,
                "message": message,
            },
        )


class APIErrorResponse(JSONResponse):
    def __init__(
        self,
        *,
        message: str,
        code: str,
        status_code: int,
    ) -> None:
        super().__init__(
            status_code=status_code,
            content={
                "success": False,
                "message": message,
                "code": code,
            },
        )


class ValidationErrorResponse(JSONResponse):
    def __init__(
        self,
        *,
        errors: dict[str, list[str]],
        message: str = "Payload Validation Failed!",
    ) -> None:
        super().__init__(
            status_code=400,
            content={
                "success": False,
                "message": message,
                "errors": errors,
            },
        )
