from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CreateListingPayload(BaseModel):
    """The text fields of a new listing; the image file itself isn't JSON
    data and is handled separately via ``request.files``."""

    title: str = Field(min_length=1, max_length=140)
    body: str = Field(min_length=1, max_length=1000)
    condition: str
    price: float = Field(gt=0)
    tags: Optional[list] = Field(default=[])


class ListListingsQuery(BaseModel):
    # Fuzzy search over title, tags and description; with it, results are
    # ordered by relevance instead of newest first.
    q: Optional[str] = Field(default=None, max_length=100)
    condition: Optional[str] = None
    # Exact tag, e.g. one of the ski tags offered in the listing form.
    tag: Optional[str] = Field(default=None, max_length=50)
    price_min: Optional[float] = None
    price_max: Optional[float] = None

    @field_validator("q", "condition", "tag", "price_min", "price_max", mode="before")
    @classmethod
    def blank_to_none(cls, value):
        if isinstance(value, str):
            value = value.strip()
        return None if value == "" else value
