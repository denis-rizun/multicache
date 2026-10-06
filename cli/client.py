from uuid import UUID

import httpx

from app.schemas import PayloadCreateRequest, PayloadCreateResponse, PayloadRetrieveResponse


class PayloadClient:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def create(self, request: PayloadCreateRequest) -> UUID:
        response = await self._http.post("/payload", json=request.model_dump(mode="json"))
        response.raise_for_status()
        return PayloadCreateResponse.model_validate_json(response.content).id

    async def retrieve(self, payload_id: UUID) -> str:
        response = await self._http.get(f"/payload/{payload_id}")
        response.raise_for_status()
        return PayloadRetrieveResponse.model_validate_json(response.content).output
