from pydantic import BaseModel, EmailStr, Field


class RegisterPayload(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    email: EmailStr
    password: str = Field(min_length=6)
    state: str = Field(min_length=1, max_length=20)
    city: str = Field(min_length=1, max_length=50)


class LoginPayload(BaseModel):
    email: EmailStr
    password: str
