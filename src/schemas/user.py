from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.entity.models import Role


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    user_email: EmailStr
    password: str = Field(min_length=6, max_length=12)


class UserDb(BaseModel):
    id: int = 1
    username: str
    user_email: EmailStr
    avatar: str
    role: Role

    model_config = ConfigDict(from_attributes=True)


class UserResponseSchema(BaseModel):
    user: UserDb
    detail: str = "User successfully created."


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    result: str


class RequestEmail(BaseModel):
    email: EmailStr


class RequestNewPassword(BaseModel):
    new_password: str = Field(min_length=6, max_length=12)
