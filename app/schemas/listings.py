from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CreateListingPayload(BaseModel):
    """The text fields of a new listing; the image file itself isn't JSON
    data and is handled separately via ``request.files``."""

    title: str = Field(min_length=1, max_length=140)
    body: str = Field(min_length=1, max_length=1000)
    condition: str
    price: float = Field(gt=0)


class ListListingsQuery(BaseModel):
    condition: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None

    @field_validator("condition", "price_min", "price_max", mode="before")
    @classmethod
    def blank_to_none(cls, value):
        return None if value == "" else value
