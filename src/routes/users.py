from fastapi import APIRouter, Depends, status, UploadFile, File, Request, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.entity.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas.user import UserDb, RequestEmail, RequestNewPassword
from src.repository import users as repositories_users
from src.services.email import send_email_reset_password

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: AsyncSession = Depends(get_db)) -> User:
    """
    The update_avatar_user function is used to update the avatar of a user.
        The function takes in an UploadFile object, which is a file that has been uploaded by the client.
        It also takes in the current_user and db objects as dependencies.

    :param file: UploadFile: Get the file that is uploaded by the user
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: A user object
    :doc-author: SergiyRus1974
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.user_email, src_url, db)
    return user


@router.post("/forgot_password")
async def forgot_password(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                          db: AsyncSession = Depends(get_db)) -> dict:
    """
    The forgot_password function is used to send an email to the user with a link that will allow them
    to reset their password. The function takes in a RequestEmail object, which contains the user's email address.
    The function then checks if there is a user associated with that email address and sends an email containing
    a link for resetting their password.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the application
    :param db: AsyncSession: Get the database session
    :return: A message to the user that a confirmation email has been sent
    :doc-author: SergiyRus1974
    """
    user = await repositories_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user:
        background_tasks.add_task(send_email_reset_password, user.user_email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.post("/reset_password/{token}")
async def reset_password(body: RequestNewPassword, token: str, db: AsyncSession = Depends(get_db)) -> dict:
    """
    The reset_password function allows a user to reset their password.

    :param body: RequestNewPassword: Get the new password from the request body
    :param token: str: Get the token from the url
    :param db: AsyncSession: Get the database connection from the dependency injection container
    :return: A dictionary with a message
    :doc-author: SergiyRus1974
    """
    email = await auth_service.get_email_from_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_password = auth_service.get_password_hash(body.new_password)
    await repositories_users.update_password(user, new_password, db)
    return {"message": "Password reset successfully"}
