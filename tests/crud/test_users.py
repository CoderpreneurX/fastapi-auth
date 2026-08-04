import pytest

from fastapi_auth.crud.users import UserCRUD
from fastapi_auth.models.user import UserStatus


@pytest.mark.asyncio
async def test_create_user(session):
    user = await UserCRUD.create(
        session,
        email="john@example.com",
        username="john",
        hashed_password="hashed_password",
    )

    assert user.id is not None
    assert user.email == "john@example.com"
    assert user.username == "john"
    assert user.status == UserStatus.ACTIVE
    assert user.is_verified is False
    assert user.is_superuser is False


@pytest.mark.asyncio
async def test_get_by_id(session):
    created = await UserCRUD.create(
        session,
        email="john@example.com",
        username="john",
        hashed_password="hashed_password",
    )

    found = await UserCRUD.get(session, created.id)

    assert found is not None
    assert found.id == created.id


@pytest.mark.asyncio
async def test_get_by_email(session):
    created = await UserCRUD.create(
        session,
        email="john@example.com",
        username="john",
        hashed_password="hashed_password",
    )

    found = await UserCRUD.get_by_email(session, created.email)

    assert found is not None
    assert found.id == created.id


@pytest.mark.asyncio
async def test_get_by_username(session):
    created = await UserCRUD.create(
        session,
        email="john@example.com",
        username="john",
        hashed_password="hashed_password",
    )

    found = await UserCRUD.get_by_username(session, "john")

    assert found is not None
    assert found.id == created.id


@pytest.mark.asyncio
async def test_exists_by_email(session):
    await UserCRUD.create(
        session,
        email="john@example.com",
        hashed_password="hashed_password",
    )

    assert await UserCRUD.exists_by_email(session, "john@example.com")
    assert not await UserCRUD.exists_by_email(session, "missing@example.com")


@pytest.mark.asyncio
async def test_exists_by_username(session):
    await UserCRUD.create(
        session,
        email="john@example.com",
        username="john",
        hashed_password="hashed_password",
    )

    assert await UserCRUD.exists_by_username(session, "john")
    assert not await UserCRUD.exists_by_username(session, "jane")


@pytest.mark.asyncio
async def test_get_active_by_email(session):
    active = await UserCRUD.create(
        session,
        email="active@example.com",
        hashed_password="pw",
    )

    deleted = await UserCRUD.create(
        session,
        email="deleted@example.com",
        hashed_password="pw",
        status=UserStatus.DELETED,
    )

    assert (await UserCRUD.get_active_by_email(session, active.email)) is not None

    assert await UserCRUD.get_active_by_email(session, deleted.email) is None


@pytest.mark.asyncio
async def test_get_active_by_id(session):
    active = await UserCRUD.create(
        session,
        email="active@example.com",
        hashed_password="pw",
    )

    deleted = await UserCRUD.create(
        session,
        email="deleted@example.com",
        hashed_password="pw",
        status=UserStatus.DELETED,
    )

    assert (await UserCRUD.get_active_by_id(session, active.id)) is not None

    assert await UserCRUD.get_active_by_id(session, deleted.id) is None


@pytest.mark.asyncio
async def test_list_users(session):
    await UserCRUD.create(
        session,
        email="a@example.com",
        hashed_password="pw",
    )

    await UserCRUD.create(
        session,
        email="b@example.com",
        hashed_password="pw",
    )

    users = await UserCRUD.list(session)

    assert len(users) >= 2


@pytest.mark.asyncio
async def test_list_users_by_status(session):
    await UserCRUD.create(
        session,
        email="active@example.com",
        hashed_password="pw",
    )

    await UserCRUD.create(
        session,
        email="deleted@example.com",
        hashed_password="pw",
        status=UserStatus.DELETED,
    )

    users = await UserCRUD.list(
        session,
        status=UserStatus.DELETED,
    )

    assert len(users) == 1
    assert users[0].status == UserStatus.DELETED


@pytest.mark.asyncio
async def test_update(session):
    user = await UserCRUD.create(
        session,
        email="john@example.com",
        hashed_password="pw",
    )

    await UserCRUD.update(
        session,
        user,
        first_name="John",
        last_name="Doe",
    )

    assert user.first_name == "John"
    assert user.last_name == "Doe"


@pytest.mark.asyncio
async def test_change_password(session):
    user = await UserCRUD.create(
        session,
        email="john@example.com",
        hashed_password="old",
    )

    await UserCRUD.change_password(
        session,
        user,
        "new_hash",
    )

    assert user.hashed_password == "new_hash"
    assert user.password_changed_at is not None


@pytest.mark.asyncio
async def test_verify(session):
    user = await UserCRUD.create(
        session,
        email="john@example.com",
        hashed_password="pw",
    )

    assert not user.is_verified

    await UserCRUD.verify(session, user)

    assert user.is_verified


@pytest.mark.asyncio
async def test_change_status(session):
    user = await UserCRUD.create(
        session,
        email="john@example.com",
        hashed_password="pw",
    )

    await UserCRUD.change_status(
        session,
        user,
        UserStatus.SUSPENDED,
    )

    assert user.status == UserStatus.SUSPENDED


@pytest.mark.asyncio
async def test_update_last_login(session):
    user = await UserCRUD.create(
        session,
        email="john@example.com",
        hashed_password="pw",
    )

    assert user.last_login_at is None

    await UserCRUD.update_last_login(session, user)

    assert user.last_login_at is not None


@pytest.mark.asyncio
async def test_soft_delete(session):
    user = await UserCRUD.create(
        session,
        email="john@example.com",
        hashed_password="pw",
    )

    await UserCRUD.soft_delete(session, user)

    assert user.status == UserStatus.DELETED
    assert user.deleted_at is not None


@pytest.mark.asyncio
async def test_delete(session):
    user = await UserCRUD.create(
        session,
        email="john@example.com",
        hashed_password="pw",
    )

    await UserCRUD.delete(session, user)

    found = await UserCRUD.get(session, user.id)

    assert found is None
