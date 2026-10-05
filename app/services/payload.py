import asyncio
from itertools import batched
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Payload, Transformation
from app.services.hash import compute_input_hash, hash_string
from app.services.transformer import Transformer

DB_BATCH_SIZE = 5_000


class PayloadService:
    def __init__(self, session: AsyncSession, transformer: Transformer) -> None:
        self._session = session
        self._transformer = transformer

    async def create(self, list_1: list[str], list_2: list[str]) -> UUID:
        input_hash = compute_input_hash(list_1, list_2)
        if existing_id := await self._get_payload_id(input_hash):
            return existing_id

        transformed = await self._transform_all({*list_1, *list_2})
        output = ", ".join(transformed[value] for pair in zip(list_1, list_2, strict=True) for value in pair)

        stmt = (
            insert(Payload)
            .values(input_hash=input_hash, output=output)
            .on_conflict_do_update(index_elements=["input_hash"], set_={"input_hash": input_hash})
            .returning(col(Payload.id))
        )
        payload_id: UUID = (await self._session.exec(stmt)).scalar_one()
        await self._session.commit()
        return payload_id

    async def retrieve(self, payload_id: UUID) -> Payload:
        payload = await self._session.get(Payload, payload_id)
        if not payload:
            raise NotFoundError("Payload not found")
        return payload

    async def _get_payload_id(self, input_hash: str) -> UUID | None:
        stmt = select(Payload.id).where(Payload.input_hash == input_hash)
        return (await self._session.exec(stmt)).first()

    async def _transform_all(self, values: set[str]) -> dict[str, str]:
        hashes = {value: hash_string(value) for value in values}

        transformed: dict[str, str] = {}
        for hash_batch in batched(hashes.values(), DB_BATCH_SIZE, strict=False):
            select_stmt = select(Transformation).where(col(Transformation.input_hash).in_(hash_batch))
            transformed.update((row.input, row.output) for row in await self._session.exec(select_stmt))

        missing = list(values - transformed.keys())
        if not missing:
            return transformed

        outputs = await asyncio.gather(*(self._transformer.uppercase(value) for value in missing))
        fresh = dict(zip(missing, outputs, strict=True))

        rows = [{"input_hash": hashes[value], "input": value, "output": output} for value, output in fresh.items()]
        for row_batch in batched(rows, DB_BATCH_SIZE, strict=False):
            insert_stmt = insert(Transformation).values(row_batch).on_conflict_do_nothing(index_elements=["input_hash"])
            await self._session.exec(insert_stmt)
        await self._session.commit()

        transformed.update(fresh)
        return transformed
