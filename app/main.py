from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette import status

from app.core.config import config
from app.core.db import dispose_engine
from app.core.exceptions import register_exception_handler
from app.core.logger import configure_logging
from app.dependencies import CreatedPayloadIdDep, PayloadDep
from app.schemas import PayloadCreateResponse, PayloadRetrieveResponse


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    configure_logging()
    logger = structlog.get_logger()
    logger.info("application started", env=config.ENV, version=config.api.VERSION)

    try:
        yield
    finally:
        await dispose_engine()
        logger.info("application ended")


app = FastAPI(
    title=config.api.NAME,
    version=config.api.VERSION,
    lifespan=lifespan,
    openapi_url=None if config.ENV == "PROD" else "/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.ALLOWED_HOSTS,
    allow_credentials=config.api.ALLOW_CREDENTIALS,
    allow_methods=config.api.ALLOWED_METHODS,
    allow_headers=config.api.ALLOWED_HEADERS,
)

register_exception_handler(app)


@app.get(path="/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    path="/payload",
    tags=["Payloads"],
    summary="Generate a payload, or reuse the identifier of an identical one",
    status_code=status.HTTP_201_CREATED,
)
async def create(payload_id: CreatedPayloadIdDep) -> PayloadCreateResponse:
    return PayloadCreateResponse(id=payload_id)


@app.get(
    path="/payload/{id}",
    tags=["Payloads"],
    summary="Retrieve a generated payload",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Payload not found"}},
)
async def retrieve(payload: PayloadDep) -> PayloadRetrieveResponse:
    return PayloadRetrieveResponse(output=payload.output)
