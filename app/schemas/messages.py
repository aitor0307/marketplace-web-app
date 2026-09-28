from typing import Optional

from pydantic import BaseModel, Field


class SendMessagePayload(BaseModel):
    subject: str = Field(min_length=1, max_length=140)
    body: str = Field(min_length=1, max_length=1000)
    listing_id: Optional[int] = Field(default=None)
