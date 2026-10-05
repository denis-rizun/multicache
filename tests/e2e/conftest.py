from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.dependencies import get_session, get_transformer
from app.main import app
from tests.fakes import FakeTransformer

BASE_URL = "http://testserver"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as http_client:
        yield http_client


@pytest.fixture
async def client_with_db(
    client: AsyncClient, db_session: AsyncSession, transformer: FakeTransformer
) -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[get_transformer] = lambda: transformer
    try:
        yield client
    finally:
        app.dependency_overrides.pop(get_session, None)
        app.dependency_overrides.pop(get_transformer, None)
