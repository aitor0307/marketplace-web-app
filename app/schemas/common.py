from typing import Optional

from pydantic import BaseModel


class UserPublic(BaseModel):
    """The shape of User.to_dict() as returned by the auth/user endpoints."""

    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    role: str


class AuthResponse(BaseModel):
    """What every login/register/oauth-login endpoint returns."""

    user: UserPublic
    access_token: str
    refresh_token: str
