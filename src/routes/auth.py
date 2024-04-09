from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as repositories_users
from src.schemas.user import UserSchema, TokenSchema, LogoutResponse, RequestEmail, UserResponseSchema
from src.entity.models import User
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=['auth'])

get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, background_tasks: BackgroundTasks, request: Request,
                 db: AsyncSession = Depends(get_db)):
    exist_user = await repositories_users.get_user_by_email(body.user_email, db)

    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.user_email, new_user.username, str(request.base_url))
    # return new_user
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


# @cache
@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.user_email})
    refresh_token_ = await auth_service.create_refresh_token(data={"sub": user.user_email})
    await repositories_users.update_token(user, refresh_token_, db)
    return {"access_token": access_token, "refresh_token": refresh_token_, "token_type": "bearer"}


@router.post("/logout", response_model=LogoutResponse)
async def logout(user: User = Depends(auth_service.get_current_user),
                 db: AsyncSession = Depends(get_db)):
    user.refresh_token = None
    await db.commit()
    return {"result": "Success"}


@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token_ = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token_, db)
    return {"access_token": access_token, "refresh_token": refresh_token_, "token_type": "bearer"}


@router.post("/request_email")
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    user = await repositories_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.user_email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}
