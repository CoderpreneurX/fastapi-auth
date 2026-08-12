from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_auth.crud.verification_tokens import VerificationTokenCRUD
from fastapi_auth.models.user import User
from fastapi_auth.models.verification_token import (
    VerificationTokenType,
)


@pytest.mark.asyncio
async def test_create_verification_token(session: AsyncSession, user: User):
    user_id = user.id
    token_hash = "hashed-token"
    token_type = VerificationTokenType.EMAIL_VERIFICATION
    expires_at = datetime.now(UTC) + timedelta(hours=1)

    token = await VerificationTokenCRUD.create(
        session,
        user_id=user_id,
        token_hash=token_hash,
        token_type=token_type,
        expires_at=expires_at,
    )

    assert token.id is not None
    assert token.user_id == user_id
    assert token.token_hash == token_hash
    assert token.token_type == token_type
    assert token.expires_at == expires_at
    assert token.used_at is None


@pytest.mark.asyncio
async def test_get_verification_token_by_hash(
    session: AsyncSession,
    user: User,
):
    user_id = user.id
    token_hash = "hashed-token"
    token_type = VerificationTokenType.EMAIL_VERIFICATION
    expires_at = datetime.now(UTC) + timedelta(hours=1)

    created_token = await VerificationTokenCRUD.create(
        session,
        user_id=user_id,
        token_hash=token_hash,
        token_type=token_type,
        expires_at=expires_at,
    )

    found_token = await VerificationTokenCRUD.get_by_hash(
        session,
        token_hash=token_hash,
        token_type=token_type,
    )

    assert found_token is not None
    assert found_token.id == created_token.id
    assert found_token.user_id == user_id
    assert found_token.token_hash == token_hash
    assert found_token.token_type == token_type


@pytest.mark.asyncio
async def test_get_verification_token_by_hash_returns_none_when_not_found(
    session: AsyncSession,
):
    result = await VerificationTokenCRUD.get_by_hash(
        session,
        token_hash="does-not-exist",
        token_type=VerificationTokenType.EMAIL_VERIFICATION,
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_verification_token_requires_matching_token_type(
    session: AsyncSession,
    user: User,
):
    user_id = user.id
    token_hash = "same-hash"
    expires_at = datetime.now(UTC) + timedelta(hours=1)

    await VerificationTokenCRUD.create(
        session,
        user_id=user_id,
        token_hash=token_hash,
        token_type=VerificationTokenType.EMAIL_VERIFICATION,
        expires_at=expires_at,
    )

    result = await VerificationTokenCRUD.get_by_hash(
        session,
        token_hash=token_hash,
        token_type=VerificationTokenType.PASSWORD_RESET,
    )

    assert result is None


@pytest.mark.asyncio
async def test_mark_verification_token_as_used(
    session: AsyncSession,
    user: User,
):
    token = await VerificationTokenCRUD.create(
        session,
        user_id=user.id,
        token_hash="hashed-token",
        token_type=VerificationTokenType.EMAIL_VERIFICATION,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )

    assert token.used_at is None

    updated_token = await VerificationTokenCRUD.mark_as_used(
        session,
        token,
    )

    assert updated_token.id == token.id
    assert updated_token.used_at is not None
    assert updated_token.used_at.tzinfo is not None


@pytest.mark.asyncio
async def test_mark_verification_token_as_used_persists(
    session: AsyncSession,
    user: User,
):
    token = await VerificationTokenCRUD.create(
        session,
        user_id=user.id,
        token_hash="hashed-token",
        token_type=VerificationTokenType.EMAIL_VERIFICATION,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )

    await VerificationTokenCRUD.mark_as_used(session, token)

    found_token = await VerificationTokenCRUD.get_by_hash(
        session,
        token_hash="hashed-token",
        token_type=VerificationTokenType.EMAIL_VERIFICATION,
    )

    assert found_token is not None
    assert found_token.used_at is not None


@pytest.mark.asyncio
async def test_create_verification_token_persists_after_commit(
    session: AsyncSession,
    user: User,
):
    token_hash = "persisted-token"

    token = await VerificationTokenCRUD.create(
        session,
        user_id=user.id,
        token_hash=token_hash,
        token_type=VerificationTokenType.EMAIL_VERIFICATION,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )

    token_id = token.id

    await session.commit()

    found_token = await VerificationTokenCRUD.get_by_hash(
        session,
        token_hash=token_hash,
        token_type=VerificationTokenType.EMAIL_VERIFICATION,
    )

    assert found_token is not None
    assert found_token.id == token_id
