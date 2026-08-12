from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_auth.config import get_settings
from fastapi_auth.crud.users import UserCRUD
from fastapi_auth.models.user import User, UserStatus
from fastapi_auth.models.verification_token import (
    VerificationTokenType,
)
from fastapi_auth.core.email import email_service
from fastapi_auth.core.hashing import Hashing
from fastapi_auth.exceptions import (
    UserAlreadyExistsError,
    InvalidVerificationTokenError,
)


def generate_verification_token() -> tuple[str, str]:
    """
    Generate the raw token and its SHA-256 hash.

    The raw token is sent by email.
    Only the hash is stored in the database.
    """
    raw_token = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    return raw_token, token_hash


def build_verification_url(raw_token: str) -> str:
    settings = get_settings()

    return f"{settings.FRONTEND_URL}/verify-email" f"?token={raw_token}"


class UserService:
    """Service responsible for user registration and verification."""

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session
        self.settings = get_settings()
        self.user_crud = UserCRUD
        self.email_service = email_service

    async def register(
        self,
        *,
        email: str,
        password: str,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        avatar_url: str | None = None,
    ) -> User:
        # ----------------------------------------------------------
        # Validate uniqueness
        # ----------------------------------------------------------

        if await self.user_crud.exists_by_email(
            self.session,
            email,
        ):
            raise UserAlreadyExistsError("A user with this email already exists.")

        if username and await self.user_crud.exists_by_username(
            self.session,
            username,
        ):
            raise UserAlreadyExistsError("A user with this username already exists.")

        # ----------------------------------------------------------
        # Create user
        # ----------------------------------------------------------

        hashed_password = Hashing.hash(password)

        user = await self.user_crud.create(
            self.session,
            email=email,
            hashed_password=hashed_password,
            username=username,
            first_name=first_name,
            last_name=last_name,
            avatar_url=avatar_url,
            status=UserStatus.ACTIVE,
            is_verified=False,
        )

        # ----------------------------------------------------------
        # Create email verification token
        # ----------------------------------------------------------

        raw_token, token_hash = generate_verification_token()

        await self.verification_token_crud.create(
            self.session,
            user_id=user.id,
            token_hash=token_hash,
            token_type=VerificationTokenType.EMAIL_VERIFICATION,
            expires_at=(
                datetime.now(UTC)
                + timedelta(
                    seconds=self.settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_SECONDS
                )
            ),
        )

        await self.session.commit()

        # ----------------------------------------------------------
        # Send verification email
        # ----------------------------------------------------------

        verification_url = build_verification_url(raw_token)

        await self.email_service.send(
            to=user.email,
            subject="Verify your email address",
            template="verify_email.html",
            context={
                "user": user,
                "verification_url": verification_url,
                "expires_in_minutes": (
                    self.settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_SECONDS // 60
                ),
            },
        )

        return user

    async def verify_email(self, raw_token: str) -> User:
        """
        Verify a user's email address using a verification token.
        """

        # Hash the raw token received from the client.
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        # Find the verification token through the token CRUD.
        verification_token = await self.verification_token_crud.get_by_hash(
            self.session,
            token_hash=token_hash,
            token_type=VerificationTokenType.EMAIL_VERIFICATION,
        )

        if verification_token is None:
            raise InvalidVerificationTokenError(
                "Invalid or expired verification token."
            )

        # Prevent token reuse.
        if verification_token.used_at is not None:
            raise InvalidVerificationTokenError(
                "Invalid or expired verification token."
            )

        # Check expiration.
        if verification_token.expires_at <= datetime.now(UTC):
            raise InvalidVerificationTokenError(
                "Invalid or expired verification token."
            )

        # Fetch the user through UserCRUD.
        user = await self.user_crud.get_by_id(
            self.session,
            verification_token.user_id,
        )

        if user is None:
            raise InvalidVerificationTokenError(
                "Invalid or expired verification token."
            )

        # Mark the user as verified through UserCRUD.
        user = await self.user_crud.verify(
            self.session,
            user,
        )

        # Mark the verification token as consumed through VerificationTokenCRUD.
        await self.verification_token_crud.mark_as_used(
            self.session,
            verification_token,
        )

        await self.session.commit()

        return user
