from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from src.entity.models import Contact
from src.schemas.contact import ContactSchema, ContactUpdateSchema


class InternalError(Exception):
    pass


def days_to_birthday(self):
    today = date.today()
    year = today.year if today <= self.replace(year=today.year) else today.year + 1
    closest_birthday = self.replace(year=year)
    return (closest_birthday - today).days


async def get_contacts_birthday(limit: int, offset: int, db: AsyncSession):
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    results = list(contacts.scalars().all())

    return [contact for contact in results if days_to_birthday(contact.birth_date) <= 7]


async def get_contacts(limit: int, offset: int, db: AsyncSession):
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contacts_first_name(first_name: str, limit: int, offset: int, db: AsyncSession):
    stmt = select(Contact).filter_by(first_name=first_name).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contacts_last_name(last_name: str, limit: int, offset: int, db: AsyncSession):
    stmt = select(Contact).filter_by(first_name=last_name).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact_email(email: str, db: AsyncSession):
    stmt = select(Contact).filter_by(email=email)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def get_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession):
    stmt = select(Contact).filter_by(email=body.email)
    result = await db.execute(stmt)
    contact_ = result.scalar_one_or_none()
    if contact_ is None:
        contact = Contact(**body.model_dump(exclude_unset=True))
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact
    return


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if contact:
        if contact.email != body.email:
            stmt = select(Contact).filter_by(email=body.email)
            result = await db.execute(stmt)
            contact_ = result.scalar_one_or_none()
            if contact_:
                return Exception
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.friend_status = body.friend_status
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact
