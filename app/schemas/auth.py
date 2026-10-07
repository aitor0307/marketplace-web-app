from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterPayload(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    email: EmailStr
    password: str = Field(min_length=6)
    state: str = Field(min_length=1, max_length=20)
    city: str = Field(min_length=1, max_length=50)
    # Optional on purpose: without the right key the account is still
    # created, just "pending" until approved.
    registration_key: Optional[str] = Field(default=None, max_length=200)


class LoginPayload(BaseModel):
    email: EmailStr
    password: str


class OAuthLoginPayload(BaseModel):
    """Registers or logs in a user via a third-party provider's ID token.

    ``provider`` isn't constrained to a fixed set here: the set of
    supported providers is the OAUTH_VERIFIERS registry in
    app/routes/operations/auth_ops.py, so adding one doesn't need a schema
    change, just another verifier function.
    """

    provider: str = Field(min_length=1, max_length=20)
    id_token: str = Field(min_length=1)
