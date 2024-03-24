from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from src.database.db import get_db
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get("/birthday", response_model=list[ContactResponse])
async def get_contacts_birthday(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                                db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contacts.get_contacts_birthday(limit, offset, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts


@router.get("/email", response_model=ContactResponse)
async def get_contact_email(email: EmailStr, db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.get_contact_email(email, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get("/first_name", response_model=list[ContactResponse])
async def get_contacts_first_name(first_name: str = Query(description="Input first name", min_length=3, max_length=50),
                                  limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                                  db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contacts.get_contacts_first_name(first_name, limit, offset, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts


@router.get("/last_name", response_model=list[ContactResponse])
async def get_contacts_last_name(last_name: str = Query(description="Input last name", min_length=3, max_length=50),
                                 limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                                 db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contacts.get_contacts_last_name(last_name, limit, offset, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.create_contact(body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="EMAIL EXISTING")
    return contact


@router.put("/{contact_id}")
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    if contact == Exception:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="EMAIL EXISTING")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    contact = await repositories_contacts.delete_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get("/", response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contacts.get_contacts(limit, offset, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts
