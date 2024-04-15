from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema
# from src.services.auth import auth_service


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)) -> User | None:
    """
    The get_user_by_email function takes in an email and returns a User object if the user exists.
    If no user is found, it returns None.

    :param email: str: Specify the email of the user to be retrieved
    :param db: AsyncSession: Pass the database session to the function
    :return: A single user or none
    :doc-author: SergiyRus1974
    """
    stmt = select(User).filter_by(user_email=email)
    user = await db.execute(stmt)
    return user.scalar_one_or_none()


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)) -> User:
    """
    The create_user function creates a new user in the database.

    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Get the database session from the dependency
    :return: A user object
    :doc-author: SergiyRus1974
    """
    avatar = None
    try:
        g = Gravatar(email=body.user_email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify the user in the database
    :param token: str | None: Update the user's refresh token
    :param db: AsyncSession: Pass the database session to the function
    :return: A boolean value
    :doc-author: SergiyRus1974
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession):
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Specify the email of the user to be confirmed
    :param db: AsyncSession: Pass the database session into the function
    :return: A boolean value
    :doc-author: SergiyRus1974
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar(email, url: str, db: AsyncSession) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: Get the user from the database
    :param url: str: Specify the type of the parameter
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    :doc-author: SergiyRus1974
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user


async def update_password(user: User, new_password: str, db: AsyncSession) -> User:
    """
    The update_password function takes a user object, a new password string, and an async database session.
    It updates the user's password to the new_password string and commits it to the database. It then refreshes
    the user object from the database so that it has all of its attributes up-to-date.

    :param user: User: Pass the user object to the function
    :param new_password: str: Pass the new password to the function
    :param db: AsyncSession: Pass the database session to the function
    :return: The updated user
    :doc-author: SergiyRus1974
    """
    user.password = new_password
    await db.commit()
    await db.refresh(user)
    return user
