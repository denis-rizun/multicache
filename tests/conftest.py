from collections.abc import AsyncIterator

import pytest
from sqlalchemy import pool, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app import models as _models
from app.core.config import config
from tests.fakes import FakeTransformer

_ = _models


@pytest.fixture(scope="session")
def test_database_url() -> str:
    url = config.database.get_test_url()
    test_db = make_url(url).database
    if not test_db:
        pytest.fail("POSTGRES_TEST_DATABASE is not configured")
    if test_db == config.database.DATABASE:
        pytest.fail(
            f"Refusing to run tests: TEST_DATABASE ({test_db!r}) "
            f"matches DATABASE ({config.database.DATABASE!r}). Tests would destroy real data."
        )
    return url


async def _ensure_database_exists(url: str) -> None:
    parsed = make_url(url)
    admin_engine = create_async_engine(
        parsed.set(database="postgres"), isolation_level="AUTOCOMMIT", poolclass=pool.NullPool
    )
    try:
        async with admin_engine.connect() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": parsed.database}
            )
            if not exists:
                await conn.execute(text(f'CREATE DATABASE "{parsed.database}"'))
    finally:
        await admin_engine.dispose()


@pytest.fixture(scope="session")
async def _bootstrap_schema(test_database_url: str) -> AsyncIterator[None]:
    await _ensure_database_exists(test_database_url)
    engine = create_async_engine(test_database_url, poolclass=pool.NullPool)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
        yield
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
    finally:
        await engine.dispose()


@pytest.fixture
async def test_engine(_bootstrap_schema: None, test_database_url: str) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(test_database_url, poolclass=pool.NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_connection(test_engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    async with test_engine.connect() as connection:
        transaction = await connection.begin()
        try:
            yield connection
        finally:
            await transaction.rollback()


@pytest.fixture
async def db_session(db_connection: AsyncConnection) -> AsyncIterator[AsyncSession]:
    session_factory = async_sessionmaker(
        bind=db_connection,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
def transformer() -> FakeTransformer:
    return FakeTransformer()
