import io
import json

import pytest
from httpx import AsyncClient

from app.schemas import PayloadCreateRequest
from cli.client import PayloadClient
from cli.runner import run
from tests.fakes import FakeTransformer

pytestmark = pytest.mark.e2e

REQUEST = PayloadCreateRequest(list_1=["first", "second"], list_2=["one", "first"])


async def run_cli(client: AsyncClient, repeat: int) -> list[dict[str, str]]:
    out = io.StringIO()
    await run(PayloadClient(client), REQUEST, repeat, out)
    return [json.loads(line) for line in out.getvalue().splitlines()]


class TestRun:
    async def test_writes_the_output_of_every_iteration(self, client_with_db: AsyncClient) -> None:
        records = await run_cli(client_with_db, repeat=3)

        assert [record["output"] for record in records] == ["FIRST, ONE, SECOND, FIRST"] * 3

    async def test_reuses_the_payload_and_transforms_each_value_once(
        self, client_with_db: AsyncClient, transformer: FakeTransformer
    ) -> None:
        records = await run_cli(client_with_db, repeat=3)

        assert len({record["id"] for record in records}) == 1
        assert sorted(transformer.calls) == ["first", "one", "second"]
