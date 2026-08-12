from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_auth.models.verification_token import (
    VerificationToken,
    VerificationTokenType,
)


class VerificationTokenCRUD:
    """CRUD operations for verification tokens."""

    @staticmethod
    async def create(
        session: AsyncSession,
        *,
        user_id: UUID,
        token_hash: str,
        token_type: VerificationTokenType,
        expires_at: datetime,
    ) -> VerificationToken:
        token = VerificationToken(
            user_id=user_id,
            token_hash=token_hash,
            token_type=token_type,
            expires_at=expires_at,
        )

        session.add(token)

        await session.flush()
        await session.refresh(token)

        return token

    @staticmethod
    async def get_by_hash(
        session: AsyncSession,
        *,
        token_hash: str,
        token_type: VerificationTokenType,
    ) -> VerificationToken | None:
        result = await session.execute(
            select(VerificationToken).where(
                VerificationToken.token_hash == token_hash,
                VerificationToken.token_type == token_type,
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def mark_as_used(
        session: AsyncSession,
        token: VerificationToken,
    ) -> VerificationToken:
        token.used_at = datetime.now(UTC)

        await session.flush()
        await session.refresh(token)

        return token
