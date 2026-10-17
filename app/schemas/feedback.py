from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class FeedbackKind(str, Enum):
    BUG = "bug"
    IMPROVEMENT = "improvement"


class SendFeedbackPayload(BaseModel):
    kind: FeedbackKind
    message: str = Field(min_length=1, max_length=2000)
    # The SPA route the user was on, to help reproduce bugs.
    page: Optional[str] = Field(default=None, max_length=500)
