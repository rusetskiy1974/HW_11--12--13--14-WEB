from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema


class InternalError(Exception):
    pass


def days_to_birthday(self) -> int:
    """
    The days_to_birthday function returns the number of days until a person's next birthday.

    :param self: Refer to the object itself
    :return: The number of days until the next birthday
    :doc-author: SergiyRus1974
    """
    today = date.today()
    year = today.year if today <= self.replace(year=today.year) else today.year + 1
    closest_birthday = self.replace(year=year)
    return (closest_birthday - today).days


async def get_contacts_birthday(limit: int, offset: int, db: AsyncSession, user: User) -> list[Contact]:
    """
    The get_contacts_birthday function returns a list of contacts whose birthdays are within the next 7 days.
        The function takes in three parameters: limit, offset, and db. Limit is an integer that specifies how many
        contacts to return at once (defaults to 10). Offset is an integer that specifies where in the database to start
        returning results from (defaults to 0). Db is a SQLAlchemy AsyncSession object which allows us access our database.

    :param limit: int: Limit the number of results returned
    :param offset: int: Specify the number of records to skip before starting to return rows
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the contacts by user
    :return: A list of contacts that have a birthday in the next 7 days
    :doc-author: SergiyRus1974
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    results = list(contacts.scalars().all())

    return [contact for contact in results if days_to_birthday(contact.birth_date) <= 7]


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User) -> Sequence[Contact]:
    """
    The get_contacts function returns a list of contacts for the given user.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip
    :param db: AsyncSession: Pass a database connection to the function
    :param user: User: Filter the results by user
    :return: A list of contact objects
    :doc-author: SergiyRus1974
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_all_contacts(limit: int, offset: int, db: AsyncSession) -> Sequence[Contact]:
    """
    The get_all_contacts function returns a list of all contacts in the database.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of rows to skip
    :param db: AsyncSession: Pass in the database session to use
    :return: A list of contacts
    :doc-author: Trelent
    """
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contacts_first_name(first_name: str, limit: int, offset: int, db: AsyncSession, user: User) -> \
        Sequence[Contact]:
    """
    The get_contacts_first_name function returns a list of contacts with the given first name.


    :param first_name: str: Filter the contacts by first name
    :param limit: int: Limit the number of results returned
    :param offset: int: Specify the number of rows to skip before starting to return rows
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the contacts by user
    :return: A list of contacts with the given first name
    :doc-author: SergiyRus1974
    """
    stmt = select(Contact).filter_by(first_name=first_name, user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contacts_last_name(last_name: str, limit: int, offset: int, db: AsyncSession, user: User) -> \
        Sequence[Contact]:
    """
    The get_contacts_last_name function returns a list of contacts with the given last name.

    :param last_name: str: Filter the contacts by last name
    :param limit: int: Limit the number of results returned
    :param offset: int: Specify the number of rows to skip
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the results by user
    :return: A list of contacts with the given last name
    :doc-author: SergiyRus1974
    """
    stmt = select(Contact).filter_by(last_name=last_name, user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact_email(email: str, db: AsyncSession, user: User) -> Contact | None:
    """
    The get_contact_email function takes in an email and a database session,
    and returns the contact associated with that email. If no such contact exists,
    it returns None.

    :param email: str: Filter the contact table by email
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the query to only return contacts for that user
    :return: A contact object
    :doc-author: SergiyRus1974
    """
    stmt = select(Contact).filter_by(email=email, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def get_contact(contact_id: int, db: AsyncSession, user: User) -> Contact | None:
    """
    The get_contact function takes in a contact_id and returns the Contact object
        associated with that id. If no such contact exists, it returns None.

    :param contact_id: int: Specify the id of the contact we want to retrieve
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Ensure that the user is only able to access their own contacts
    :return: A contact object if a contact with the given id exists for the given user
    :doc-author: SergiyRus1974
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User) -> Contact | None:
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user that is currently logged in
    :return: A contact object if the contact is created, or none if it already exists
    :doc-author: SergiyRus1974
    """
    stmt = select(Contact).filter_by(email=body.email, user=user)
    result = await db.execute(stmt)
    contact_ = result.scalar_one_or_none()
    if contact_ is None:
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact
    return


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User) -> \
        Contact | None | bool:
    """
    The update_contact function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactUpdateSchema): A schema containing all fields that can be updated for a Contact object.
            This is used to validate and deserialize the request body into an object that can be passed as an argument
            to this function. See schemas/contact_update_schema for more information on what fields are required, optional, etc...

    :param contact_id: int: Specify the contact that will be updated
    :param body: ContactUpdateSchema: Validate the body of the request
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Make sure that the user who is trying to update a contact is the owner of
    :return: The contact object with the updated fields
    :doc-author: SergiyRus1974
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()

    if contact:
        if contact.email != body.email:
            stmt = select(Contact).filter_by(email=body.email)
            result = await db.execute(stmt)
            contact_ = result.scalar_one_or_none()
            if contact_:
                return False
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.friend_status = body.friend_status
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User) -> Contact:
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Identify the contact to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Ensure that the user is authorized to delete the contact
    :return: The contact that was deleted
    :doc-author: SergiyRus1974
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact
