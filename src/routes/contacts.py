from typing import Sequence

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from src.database.db import get_db
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactUpdateSchema, ContactResponse
from src.services.auth import auth_service
from src.entity.models import User, Role, Contact
from src.services.roles import RoleAccess


router = APIRouter(prefix='/contacts', tags=['contacts'])
access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/all", response_model=list[ContactResponse], dependencies=[Depends(access_to_route_all)])
async def get_all_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)) -> \
        Sequence[Contact]:
    """
    The get_all_contacts function returns a list of contacts.

    :param limit: int: Limit the number of contacts returned
    :param ge: Check that the limit is greater than or equal to 10
    :param le: Limit the number of contacts returned to a maximum of 500
    :param offset: int: Specify the number of records to skip before starting to return the results
    :param ge: Check if the value is greater than or equal to 10
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A list of contacts
    :doc-author: SergiyRus1974
    """
    contacts = await repositories_contacts.get_all_contacts(limit, offset, db)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts


@router.get("/birthday", response_model=list[ContactResponse])
async def get_contacts_birthday(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                                db: AsyncSession = Depends(get_db),
                                user: User = Depends(auth_service.get_current_user)) -> Sequence[Contact]:
    """
    The get_contacts_birthday function returns a list of contacts that have birthdays in the next 7 days.
    The function takes an optional limit and offset parameter to control how many results are returned.
    The user must be logged in to use this function.

    :param limit: int: Limit the number of contacts returned
    :param ge: Specify a minimum value, and the le parameter is used to specify a maximum value
    :param le: Limit the maximum value of the parameter
    :param offset: int: Skip a number of records in the database
    :param ge: Set a minimum value for the parameter
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the auth_service
    :return: A list of contacts who have a birthday in the current month
    :doc-author: SergiyRus1974
    """
    contacts = await repositories_contacts.get_contacts_birthday(limit, offset, db, user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts


@router.get("/email", response_model=ContactResponse)
async def get_contact_email(email: EmailStr, db: AsyncSession = Depends(get_db),
                            user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    The get_contact_email function is used to retrieve a contact by email.
        The function takes in an email and returns the contact associated with that email.

    :param email: EmailStr: Get the email from the request body
    :param db: AsyncSession: Pass a database session to the function
    :param user: User: Get the current user
    :return: A contact object
    :doc-author: SergiyRus1974
    """
    contact = await repositories_contacts.get_contact_email(email, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get("/first_name", response_model=list[ContactResponse])
async def get_contacts_first_name(first_name: str = Query(description="Input first name", min_length=3, max_length=50),
                                  limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                                  db: AsyncSession = Depends(get_db),
                                  user: User = Depends(auth_service.get_current_user)) -> Sequence[Contact]:
    """
    The get_contacts_first_name function is used to retrieve a list of contacts from the database.
    The function takes in an optional first_name parameter, which is used to filter the results by first name.
    The function also takes in two optional parameters: limit and offset, which are used for pagination purposes.
    If no limit or offset parameters are provided, then the default values will be 10 and 0 respectively.

    :param first_name: str: Get the first name from the request
    :param min_length: Set the minimum length of a string
    :param max_length: Limit the length of the first name
    :param limit: int: Limit the number of contacts returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Limit the amount of contacts returned
    :param offset: int: Specify the number of records to skip before starting to return rows
    :param ge: Specify a minimum value for the parameter
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A list of contacts
    :doc-author: SergiyRus1974
    """
    contacts = await repositories_contacts.get_contacts_first_name(first_name, limit, offset, db, user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts


@router.get("/last_name", response_model=list[ContactResponse])
async def get_contacts_last_name(last_name: str = Query(description="Input last name", min_length=3, max_length=50),
                                 limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                                 db: AsyncSession = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)) -> Sequence[Contact]:
    """
    The get_contacts_last_name function is used to retrieve a list of contacts with the same last name.
    The function takes in an optional query parameter called last_name, which is a string that represents the contact's
    last name. The function also takes in two optional query parameters called limit and offset, which are integers that
    represent how many contacts should be returned and where to start returning them from respectively. The function also
    takes in an optional dependency parameter called db, which represents the database connection pool for asyncpg. Finally,
    the function takes in an optional dependency parameter called user, which represents the current logged-in user making

    :param last_name: str: Get the last name of a contact
    :param min_length: Set the minimum length of the last name
    :param max_length: Limit the length of the input string
    :param limit: int: Limit the number of contacts returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip
    :param ge: Specify that the limit parameter must be greater than or equal to 10
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A list of contacts with the specified last name
    :doc-author: SergiyRus1974
    """
    contacts = await repositories_contacts.get_contacts_last_name(last_name, limit, offset, db, user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    The get_contact function is a GET request that returns the contact with the given ID.
    If no such contact exists, it will return a 404 NOT FOUND error.

    :param contact_id: int: Specify the contact id
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A contact object
    :doc-author: SergiyRus1974
    """
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post("/", response_model=ContactResponse, description='No more than 5 requests per minute',
             dependencies=[Depends(RateLimiter(times=5, seconds=60))], status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    The create_contact function creates a new contact in the database.
        It takes an email, first_name and last_name as input parameters.
        The function returns the newly created contact object.

    :param body: ContactSchema: Validate the data that is passed in the request body
    :param db: AsyncSession: Pass the database session into the function
    :param user: User: Get the current user from the database
    :return: A contact object
    :doc-author: SergiyRus1974
    """
    contact = await repositories_contacts.create_contact(body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="EMAIL EXISTING")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactUpdateSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    The update_contact function updates a contact in the database.
        The function takes an id of the contact to be updated, and a body containing all fields that need to be updated.
        If no such contact exists, it returns 404 NOT FOUND.


    :param body: ContactUpdateSchema: Get the data from the request body
    :param contact_id: int: Get the id of the contact to be deleted
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A contact object
    :doc-author: SergiyRus1974
    """
    contact = await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    if not contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="EMAIL EXISTING")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact from the database.
        The function takes in an integer representing the id of the contact to be deleted,
        and returns a dictionary containing information about that contact.

    :param contact_id: int: Specify the contact id that will be deleted
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A contact object, but we don't need it
    :doc-author: Trelent
    """
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get("/", response_model=list[ContactResponse], description='No more than 5 requests per minute',
            dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)) -> \
        Sequence[Contact]:
    """
    The get_contacts function returns a list of contacts.

    :param limit: int: Limit the number of contacts returned
    :param ge: Specify the minimum value of the limit parameter
    :param le: Specify the maximum value of the limit parameter
    :param offset: int: Specify the offset of the first contact to return
    :param ge: Specify a minimum value
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: A list of contacts
    :doc-author: SergiyRus1974
    """
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts
