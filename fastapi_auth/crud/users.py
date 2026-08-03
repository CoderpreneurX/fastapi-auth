from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_auth.models.user import User, UserStatus


class UserCRUD:
    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    @staticmethod
    async def create(
        session: AsyncSession,
        *,
        email: str,
        hashed_password: str,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        avatar_url: str | None = None,
        status: UserStatus = UserStatus.ACTIVE,
        is_verified: bool = False,
        is_superuser: bool = False,
    ) -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            username=username,
            first_name=first_name,
            last_name=last_name,
            avatar_url=avatar_url,
            status=status,
            is_verified=is_verified,
            is_superuser=is_superuser,
        )

        session.add(user)
        await session.flush()
        await session.refresh(user)

        return user

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    @staticmethod
    async def get(
        session: AsyncSession,
        user_id: uuid.UUID,
    ) -> User | None:
        return await session.get(User, user_id)

    @staticmethod
    async def get_by_email(
        session: AsyncSession,
        email: str,
    ) -> User | None:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(
        session: AsyncSession,
        username: str,
    ) -> User | None:
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def exists_by_email(
        session: AsyncSession,
        email: str,
    ) -> bool:
        return (await UserCRUD.get_by_email(session, email)) is not None

    @staticmethod
    async def exists_by_username(
        session: AsyncSession,
        username: str,
    ) -> bool:
        return (await UserCRUD.get_by_username(session, username)) is not None

    @staticmethod
    async def get_active_by_email(
        session: AsyncSession,
        email: str,
    ) -> User | None:
        result = await session.execute(
            select(User).where(
                User.email == email,
                User.status == UserStatus.ACTIVE,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_by_id(
        session: AsyncSession,
        user_id: uuid.UUID,
    ) -> User | None:
        result = await session.execute(
            select(User).where(
                User.id == user_id,
                User.status == UserStatus.ACTIVE,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        session: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 100,
        status: UserStatus | None = None,
    ) -> list[User]:
        stmt = select(User)

        if status is not None:
            stmt = stmt.where(User.status == status)

        stmt = stmt.offset(offset).limit(limit)

        result = await session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    @staticmethod
    async def update(
        session: AsyncSession,
        user: User,
        **fields,
    ) -> User:
        for field, value in fields.items():
            if hasattr(user, field):
                setattr(user, field, value)

        await session.flush()
        await session.refresh(user)

        return user

    @staticmethod
    async def update_last_login(
        session: AsyncSession,
        user: User,
    ) -> User:
        user.last_login_at = datetime.now(UTC)

        await session.flush()
        await session.refresh(user)

        return user

    @staticmethod
    async def change_password(
        session: AsyncSession,
        user: User,
        hashed_password: str,
    ) -> User:
        user.hashed_password = hashed_password
        user.password_changed_at = datetime.now(UTC)

        await session.flush()
        await session.refresh(user)

        return user

    @staticmethod
    async def verify(
        session: AsyncSession,
        user: User,
    ) -> User:
        user.is_verified = True

        await session.flush()
        await session.refresh(user)

        return user

    @staticmethod
    async def change_status(
        session: AsyncSession,
        user: User,
        status: UserStatus,
    ) -> User:
        user.status = status

        await session.flush()
        await session.refresh(user)

        return user

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    @staticmethod
    async def soft_delete(
        session: AsyncSession,
        user: User,
    ) -> User:
        user.status = UserStatus.DELETED
        user.deleted_at = datetime.now(UTC)

        await session.flush()
        await session.refresh(user)

        return user

    @staticmethod
    async def delete(
        session: AsyncSession,
        user: User,
    ) -> None:
        await session.delete(user)
        await session.flush()
