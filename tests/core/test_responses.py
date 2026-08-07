from fastapi_auth.core.responses import (
    APIErrorResponse,
    APIResponse,
    ValidationErrorResponse,
)


async def test_api_response(client, app):
    @app.get("/success")
    async def success():
        return APIResponse(
            data={"id": 1, "name": "John"},
            message="Success",
        )

    response = await client.get("/success")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "id": 1,
            "name": "John",
        },
        "message": "Success",
    }


async def test_api_response_custom_status_code(client, app):
    @app.post("/created")
    async def created():
        return APIResponse(
            data={"id": 1},
            message="Created",
            status_code=201,
        )

    response = await client.post("/created")

    assert response.status_code == 201
    assert response.json() == {
        "success": True,
        "data": {
            "id": 1,
        },
        "message": "Created",
    }


async def test_api_error_response(client, app):
    @app.get("/error")
    async def error():
        return APIErrorResponse(
            message="User not found.",
            code="USER_NOT_FOUND",
            status_code=404,
        )

    response = await client.get("/error")

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "message": "User not found.",
        "code": "USER_NOT_FOUND",
    }


async def test_validation_error_response(client, app):
    @app.get("/validation")
    async def validation():
        return ValidationErrorResponse(
            errors={
                "email": ["Field required"],
                "password": ["Field required"],
            }
        )

    response = await client.get("/validation")

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "message": "Payload Validation Failed!",
        "errors": {
            "email": ["Field required"],
            "password": ["Field required"],
        },
    }


async def test_validation_error_response_custom_message(client, app):
    @app.get("/validation-custom")
    async def validation():
        return ValidationErrorResponse(
            message="Invalid request.",
            errors={
                "email": ["Invalid email address"],
            },
        )

    response = await client.get("/validation-custom")

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "message": "Invalid request.",
        "errors": {
            "email": ["Invalid email address"],
        },
    }
