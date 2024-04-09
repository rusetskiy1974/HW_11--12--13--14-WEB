from typing import Optional
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from src.schemas.user import UserDb


class ContactSchema(BaseModel):
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=60)
    email: EmailStr
    phone: str = Field(pattern=r"^\+?3?8?(0\d{9})$")
    birth_date: date
    friend_status: Optional[bool] = False


class ContactUpdateSchema(ContactSchema):
    friend_status: bool


class ContactResponse(BaseModel):
    id: int = 1
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birth_date: date
    friend_status: bool
    created_at: datetime | None
    updated_at: datetime | None
    user: UserDb | None

    class Config:
        from_attributes = True
