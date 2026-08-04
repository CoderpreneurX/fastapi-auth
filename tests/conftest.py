from pathlib import Path
import asyncio

import httpx
import pytest_asyncio
import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config

from fastapi_auth.database.session import AsyncSessionLocal, engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ALEMBIC_INI = PROJECT_ROOT / "fastapi_auth" / "alembic.ini"

MAILPIT_API_URL = "http://localhost:8025/api/v1"

alembic_cfg = Config(str(ALEMBIC_INI))


@pytest.fixture(scope="session", autouse=True)
def migrated_database():
    """
    Create a fresh schema before the test session and
    remove it afterwards.
    """

    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")

    yield

    command.downgrade(alembic_cfg, "base")


@pytest_asyncio.fixture
async def session():
    """
    Fresh AsyncSession for every test.
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            if session.in_transaction():
                await session.rollback()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def cleanup_engine():
    """
    Dispose the connection pool after the test session.
    """

    yield

    await engine.dispose()


@pytest_asyncio.fixture
async def mailpit():
    async with httpx.AsyncClient(
        base_url=MAILPIT_API_URL,
        timeout=5.0,
    ) as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def clear_mailpit(mailpit):
    """
    Start each test with an empty inbox.
    """
    await mailpit.delete("/messages")
    yield


@pytest_asyncio.fixture
async def mailpit_messages(mailpit):
    async def _messages():
        response = await mailpit.get("/messages")
        response.raise_for_status()
        return response.json()["messages"]

    return _messages


@pytest_asyncio.fixture
async def mailpit_message(mailpit):
    async def _message(message_id: str):
        response = await mailpit.get(f"/message/{message_id}")
        response.raise_for_status()
        return response.json()

    return _message


@pytest_asyncio.fixture
async def wait_for_email(mailpit):
    async def _wait(timeout: float = 5.0):
        deadline = asyncio.get_running_loop().time() + timeout

        while asyncio.get_running_loop().time() < deadline:
            response = await mailpit.get("/messages")
            response.raise_for_status()

            messages = response.json()["messages"]
            if messages:
                return messages

            await asyncio.sleep(0.05)

        raise AssertionError("Timed out waiting for email.")

    return _wait
