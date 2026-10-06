from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import async_session
from app.models import Payload
from app.services.payload import PayloadService
from app.services.transformer import Transformer


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session


def get_transformer() -> Transformer:
    return Transformer()


SessionDep = Annotated[AsyncSession, Depends(get_session)]
TransformerDep = Annotated[Transformer, Depends(get_transformer)]


async def get_payload_service(session: SessionDep, transformer: TransformerDep) -> PayloadService:
    return PayloadService(session, transformer)


PayloadServiceDep = Annotated[PayloadService, Depends(get_payload_service)]


async def get_payload(id: UUID, service: PayloadServiceDep) -> Payload:
    return await service.retrieve(id)


PayloadDep = Annotated[Payload, Depends(get_payload)]
