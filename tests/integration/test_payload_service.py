from uuid import uuid4

import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Transformation
from app.services.payload import PayloadService
from tests.fakes import FakeTransformer

pytestmark = pytest.mark.integration


@pytest.fixture
def service(db_session: AsyncSession, transformer: FakeTransformer) -> PayloadService:
    return PayloadService(db_session, transformer)


class TestCreate:
    async def test_stores_the_interleaved_transformed_output(self, service: PayloadService) -> None:
        payload_id = await service.create(["first", "second"], ["one", "two"])

        payload = await service.retrieve(payload_id)

        assert payload.output == "FIRST, ONE, SECOND, TWO"

    async def test_reuses_the_id_of_an_identical_payload(self, service: PayloadService) -> None:
        first_id = await service.create(["a", "b"], ["x", "y"])

        assert await service.create(["a", "b"], ["x", "y"]) == first_id

    async def test_skips_the_transformer_for_an_identical_payload(
        self, service: PayloadService, transformer: FakeTransformer
    ) -> None:
        await service.create(["a"], ["x"])
        transformer.calls.clear()

        await service.create(["a"], ["x"])

        assert transformer.calls == []

    async def test_treats_a_reordered_request_as_a_new_payload(self, service: PayloadService) -> None:
        first_id = await service.create(["a", "b"], ["x", "y"])

        assert await service.create(["b", "a"], ["y", "x"]) != first_id

    async def test_transforms_only_values_missing_from_the_cache(
        self, service: PayloadService, transformer: FakeTransformer
    ) -> None:
        await service.create(["a", "b"], ["x", "y"])
        transformer.calls.clear()

        await service.create(["a", "c"], ["x", "z"])

        assert sorted(transformer.calls) == ["c", "z"]

    async def test_transforms_a_repeated_value_once(
        self, service: PayloadService, transformer: FakeTransformer
    ) -> None:
        await service.create(["a", "a"], ["a", "b"])

        assert sorted(transformer.calls) == ["a", "b"]

    async def test_caches_every_transformed_value(self, service: PayloadService, db_session: AsyncSession) -> None:
        await service.create(["a"], ["x"])

        rows = (await db_session.exec(select(Transformation))).all()

        assert sorted((row.input, row.output) for row in rows) == [("a", "A"), ("x", "X")]


class TestRetrieve:
    async def test_returns_a_stored_payload(self, service: PayloadService) -> None:
        payload_id = await service.create(["a"], ["x"])

        payload = await service.retrieve(payload_id)

        assert (payload.id, payload.output) == (payload_id, "A, X")

    async def test_rejects_an_unknown_id(self, service: PayloadService) -> None:
        with pytest.raises(NotFoundError):
            await service.retrieve(uuid4())
