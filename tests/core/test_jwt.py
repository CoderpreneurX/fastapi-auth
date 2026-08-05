from datetime import timedelta

from fastapi_auth.core.jwt import JWT


class DummyUser:
    id = 123
    email = "john@example.com"
    role = "admin"


def test_encode_decode():
    user = DummyUser()

    token = JWT.encode(
        user,
        fields=("id", "email", "role"),
    )

    payload = JWT.decode(token)

    assert payload["id"] == 123
    assert payload["email"] == "john@example.com"
    assert payload["role"] == "admin"


def test_only_requested_fields_are_present():
    user = DummyUser()

    token = JWT.encode(
        user,
        fields=("id",),
    )

    payload = JWT.decode(token)

    assert payload["id"] == 123
    assert "email" not in payload
    assert "role" not in payload


def test_custom_claims():
    user = DummyUser()

    token = JWT.encode(
        user,
        fields=("id",),
        additional_claims={
            "type": "access",
        },
    )

    payload = JWT.decode(token)

    assert payload["type"] == "access"


def test_custom_expiry():
    user = DummyUser()

    token = JWT.encode(
        user,
        fields=("id",),
        expires_in=timedelta(minutes=30),
    )

    payload = JWT.decode(token)

    assert payload["exp"] > payload["iat"]


def test_standard_claims_exist():
    user = DummyUser()

    token = JWT.encode(
        user,
        fields=("id",),
    )

    payload = JWT.decode(token)

    assert "iat" in payload
    assert "nbf" in payload
    assert "exp" in payload
