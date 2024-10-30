from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from ..core.schemas import TimestampSchema


class TierBase(BaseModel):
    name: Annotated[str, Field(examples=["free"])]


class Tier(TimestampSchema, TierBase):
    pass


class TierRead(TierBase):
    """
    Inherits from `TierBase` and defines two attributes:
    `id` and `created_at`, which are an integer and a datetime object, respectively.

    Attributes:
        id (int): A unique identifier for the tier.
        created_at (datetime): A timestamp representing the date and time when the
            tier was created.

    """
    id: int
    created_at: datetime


class TierCreate(TierBase):
    pass


class TierCreateInternal(TierCreate):
    pass


class TierUpdate(BaseModel):
    name: str | None = None


class TierUpdateInternal(TierUpdate):
    updated_at: datetime


class TierDelete(BaseModel):
    pass
