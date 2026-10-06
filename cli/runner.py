import json
from typing import TextIO

from app.schemas import PayloadCreateRequest
from cli.client import PayloadClient


async def run(client: PayloadClient, request: PayloadCreateRequest, repeat: int, out: TextIO) -> None:
    for _ in range(repeat):
        payload_id = await client.create(request)
        output = await client.retrieve(payload_id)
        out.write(json.dumps({"id": str(payload_id), "output": output}) + "\n")
