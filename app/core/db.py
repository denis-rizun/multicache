from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import config

engine = create_async_engine(
    url=config.database.get_url(),
    echo=config.ENV == "DEV",
    pool_size=config.database.POOL_SIZE,
    pool_timeout=config.database.POOL_TIMEOUT_S,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def dispose_engine() -> None:
    await engine.dispose()
