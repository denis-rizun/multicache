from typing import Any

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.e2e

PAYLOAD = {"list_1": ["first", "second"], "list_2": ["one", "two"]}


async def create(client: AsyncClient, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    response = await client.post("/payload", json=payload or PAYLOAD)
    return response.json()  # type: ignore[no-any-return]


class TestCreatePayload:
    async def test_creates_a_new_payload(self, client_with_db: AsyncClient) -> None:
        response = await client_with_db.post("/payload", json=PAYLOAD)

        assert (response.status_code, response.json()["message"]) == (201, "Payload created")

    async def test_returns_the_same_id_for_an_identical_request(self, client_with_db: AsyncClient) -> None:
        created = await create(client_with_db)

        response = await client_with_db.post("/payload", json=PAYLOAD)

        assert (response.status_code, response.json()["id"]) == (201, created["id"])

    @pytest.mark.parametrize(
        "payload",
        [
            {"list_1": ["a", "b"], "list_2": ["x"]},
            {"list_1": [], "list_2": []},
            {"list_1": ["a"]},
            {"list_1": [1], "list_2": ["x"]},
        ],
    )
    async def test_rejects_an_invalid_payload(self, client_with_db: AsyncClient, payload: dict[str, Any]) -> None:
        response = await client_with_db.post("/payload", json=payload)

        assert response.status_code == 422


class TestRetrievePayload:
    async def test_returns_the_generated_output(self, client_with_db: AsyncClient) -> None:
        created = await create(client_with_db)

        response = await client_with_db.get(f"/payload/{created['id']}")

        assert (response.status_code, response.json()) == (200, {"output": "FIRST, ONE, SECOND, TWO"})

    async def test_rejects_an_unknown_payload(self, client_with_db: AsyncClient) -> None:
        response = await client_with_db.get("/payload/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404

    async def test_rejects_a_malformed_id(self, client_with_db: AsyncClient) -> None:
        response = await client_with_db.get("/payload/not-a-uuid")

        assert response.status_code == 422
