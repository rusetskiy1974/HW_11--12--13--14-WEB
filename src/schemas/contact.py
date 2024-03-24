from typing import Optional
from datetime import date

from pydantic import BaseModel, EmailStr, Field


class ContactSchema(BaseModel):
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=60)
    email: EmailStr
    phone: str = Field(pattern=r"^\+?3?8?(0\d{9})$")
    birth_date: date
    friend_status: Optional[bool] = False


class ContactUpdateSchema(ContactSchema):
    friend_status: bool


class ContactResponse(ContactSchema):
    id: int = 1

    class Config:
        from_attributes = True
