from fastapi import Body
from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    age: int


class StrictUserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    age: int


async def test_missing_required_field_returns_400(app, client):
    @app.post("/users")
    async def create_user(user: UserCreate):
        return {}

    response = await client.post(
        "/users",
        json={"username": "john"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "success": False,
        "message": "Payload Validation Failed!",
        "errors": {
            "age": ["Field required"],
        },
    }


async def test_invalid_type_returns_400(app, client):
    @app.post("/users")
    async def create_user(user: UserCreate):
        return {}

    response = await client.post(
        "/users",
        json={
            "username": "john",
            "age": "abc",
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Payload Validation Failed!"
    assert body["errors"]["age"][0].startswith("Input should be a valid integer")


async def test_extra_fields_return_400(app, client):
    @app.post("/strict-users")
    async def create_user(user: StrictUserCreate):
        return {}

    response = await client.post(
        "/strict-users",
        json={
            "username": "john",
            "age": 20,
            "email": "john@example.com",
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["success"] is False
    assert body["message"] == "Payload Validation Failed!"
    assert body["errors"] == {
        "email": ["Extra inputs are not permitted"],
    }


async def test_nested_validation_errors(app, client):
    class Address(BaseModel):
        city: str

    class User(BaseModel):
        address: Address

    @app.post("/nested")
    async def nested(user: User):
        return {}

    response = await client.post(
        "/nested",
        json={
            "address": {},
        },
    )

    assert response.status_code == 400

    body = response.json()

    assert body["errors"] == {
        "address.city": ["Field required"],
    }


async def test_multiple_validation_errors(app, client):
    @app.post("/multi")
    async def multi(user: UserCreate):
        return {}

    response = await client.post(
        "/multi",
        json={},
    )

    assert response.status_code == 400

    body = response.json()

    assert body["errors"] == {
        "username": ["Field required"],
        "age": ["Field required"],
    }


async def test_query_parameter_validation(app, client):
    @app.get("/query")
    async def query(age: int):
        return {}

    response = await client.get("/query?age=abc")

    assert response.status_code == 400

    body = response.json()

    assert body["errors"]["age"][0].startswith("Input should be a valid integer")
