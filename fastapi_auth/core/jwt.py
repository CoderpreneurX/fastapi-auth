from datetime import datetime, timedelta, timezone
from typing import Any, Mapping, Sequence

from jose import jwt

from fastapi_auth.config import get_settings

settings = get_settings()


class JWT:
    """Utility for encoding and decoding JSON Web Tokens."""

    @classmethod
    def encode(
        cls,
        obj: Any,
        *,
        fields: Sequence[str],
        expires_in: timedelta | None = None,
        additional_claims: Mapping[str, Any] | None = None,
    ) -> str:
        """
        Encode an object's attributes into a signed JWT.

        Args:
            obj: Object whose attributes will be serialized as JWT claims.
            fields: Names of the object's attributes to include in the payload.
            expires_in: Lifetime of the token. If omitted, the configured default
                expiry is used.
            additional_claims: Additional JWT claims to merge into the payload.

        Returns:
            The encoded JWT as a string.
        """
        now = datetime.now(timezone.utc)

        payload = {field: getattr(obj, field) for field in fields}

        payload.update(
            {
                "iat": now,
                "nbf": now,
                "exp": now
                + (expires_in or timedelta(seconds=settings.JWT_EXPIRY_SECONDS)),
                "iss": settings.JWT_ISSUER,
            }
        )

        if settings.JWT_AUDIENCE:
            payload["aud"] = settings.JWT_AUDIENCE

        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    @classmethod
    def decode(cls, token: str) -> dict[str, Any]:
        """
        Decode and validate a JWT.

        Args:
            token: The JWT to decode.

        Returns:
            The decoded JWT payload.

        Raises:
            jose.exceptions.JWTError: If the token is invalid or cannot be
                verified.
            jose.exceptions.ExpiredSignatureError: If the token has expired.
        """
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
