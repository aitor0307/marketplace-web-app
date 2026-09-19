from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UpdateUserPayload(BaseModel):
    """Every field is optional: this is a partial profile update."""

    name: Optional[str] = Field(None, min_length=1, max_length=30)
    email: Optional[EmailStr] = None
    state: Optional[str] = Field(None, min_length=1, max_length=20)
    city: Optional[str] = Field(None, min_length=1, max_length=50)
