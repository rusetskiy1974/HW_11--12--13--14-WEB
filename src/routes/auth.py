from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas.user import UserSchema, TokenSchema, LogoutResponse, RequestEmail, UserResponseSchema
from src.entity.models import User
from src.services.auth import auth_service
from src.services.email import send_email
from src.conf import messages

router = APIRouter(prefix='/auth', tags=['auth'])

get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, background_tasks: BackgroundTasks, request: Request,
                 db: AsyncSession = Depends(get_db)) -> dict:
    """
    The signup function creates a new user in the database.
        It takes in a UserSchema object, which is validated by pydantic.
        If the email already exists, it returns an HTTP 409 error code (conflict).
        Otherwise, it hashes the password and saves to database.

    :param body: UserSchema: Validate the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: AsyncSession: Get the database session
    :return: A dictionary with the user and a message
    :doc-author: SergiyRus1974
    """
    exist_user = await repository_users.get_user_by_email(body.user_email, db)

    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXISTS)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.user_email, new_user.username, str(request.base_url))
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) -> dict():
    """
    The login function is used to authenticate a user.
        It takes in the username and password of the user, and returns an access token if successful.
        The access token can be used to make authenticated requests.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: AsyncSession: Get the database session
    :return: A dict with the access token and refresh token
    :doc-author: SergiyRus1974
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.NOT_CONFIRMED_EMAIL)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD)
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.user_email})
    refresh_token_ = await auth_service.create_refresh_token(data={"sub": user.user_email})
    await repository_users.update_token(user, refresh_token_, db)
    return {"access_token": access_token, "refresh_token": refresh_token_, "token_type": "bearer"}


@router.post("/logout", response_model=LogoutResponse)
async def logout(user: User = Depends(auth_service.get_current_user),
                 db: AsyncSession = Depends(get_db)) -> dict:
    """
    The logout function will logout the user by removing their refresh token from the database.

    :param user: User: Get the current user
    :param db: AsyncSession: Access the database
    :return: A response with a dictionary containing the result
    :doc-author: SergiyRus1974
    """
    user.refresh_token = None
    await db.commit()
    return {"result": "Success"}


@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
                        db: AsyncSession = Depends(get_db)) -> dict():
    """
    The refresh_token function is used to refresh the access token.
    It takes in a refresh token and returns a new access_token and refresh_token pair.
    The function first decodes the given refresh token to get the email of its owner, then it gets that user from
    the database, checks if their stored tokens match with what was provided, if not it raises an error. If they do match
    it creates new tokens for them using auth_service's create functions and updates their stored tokens in the database.

    :param credentials: HTTPAuthorizationCredentials: Get the token from the header
    :param db: AsyncSession: Get the database session
    :return: A dict with the access_token, refresh_token and token type
    :doc-author: SergiyRus1974
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_REFRESH_TOKEN)

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token_ = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token_, db)
    return {"access_token": access_token, "refresh_token": refresh_token_, "token_type": "bearer"}


@router.post("/request_email")
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)) -> dict:
    """
    The request_email function is used to send an email to the user with a link that will allow them
    to confirm their email address. The function takes in a RequestEmail object, which contains the
    email of the user who wants to confirm their account. It then checks if there is already a confirmed
    user with that email address, and if so returns an error message saying as much. If not, it sends
    an asynchronous task (send_email) containing information about what URL should be sent in order for
    the user's account to be confirmed.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the application
    :param db: AsyncSession: Get the database session
    :return: A dict with a message key and value
    :doc-author: SergiyRus1974
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": messages.EMAIL_ALREADY_CONFIRMED}
    if user:
        background_tasks.add_task(send_email, user.user_email, user.username, str(request.base_url))
    return {"message": messages.CHECK_EMAIL_FOR_CONFIRMATION}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)) -> dict:
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        The function then checks if there is a user with that email in our database, and if not, returns an error message.
        If there is a user with that email in our database, we check whether their account has already been confirmed or not.
        If it has been confirmed already, we return an appropriate message; otherwise we update their account status.

    :param token: str: Get the token from the url
    :param db: AsyncSession: Get the database session
    :return: A dict with a message
    :doc-author: SergiyRus1974
    """

    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}
