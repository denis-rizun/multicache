from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class PayloadCreateRequest(BaseModel):
    list_1: list[str] = Field(min_length=1)
    list_2: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def check_same_length(self) -> Self:
        if len(self.list_1) != len(self.list_2):
            raise ValueError("list_1 and list_2 must have same length")
        return self


class PayloadCreateResponse(BaseModel):
    id: UUID
    message: str = "Payload created"


class PayloadRetrieveResponse(BaseModel):
    output: str
