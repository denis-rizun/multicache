from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


class Transformation(SQLModel, table=True):
    __tablename__ = "transformation_cache"

    input_hash: str = Field(primary_key=True)
    input: str
    output: str


class Payload(SQLModel, table=True):
    __tablename__ = "payload"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    input_hash: str = Field(unique=True, index=True)
    output: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        sa_type=DateTime(timezone=True),  # type: ignore[call-overload]
    )
