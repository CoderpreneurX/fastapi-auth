from pathlib import Path

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config

from fastapi_auth.database.session import AsyncSessionLocal, engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ALEMBIC_INI = PROJECT_ROOT / "fastapi_auth" / "alembic.ini"

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
