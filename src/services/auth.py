from datetime import datetime, timedelta
from typing import Optional
from src.conf.config import settings

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.repository import users as repositories_users
from src.entity.models import User


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    def verify_password(self, plain_password, hashed_password) -> bool:
        """
        The verify_password function takes a plain-text password and hashed
        password as arguments. It then uses the pwd_context object to verify that the
        plain-text password matches the hashed one.

        :param self: Represent the instance of the class
        :param plain_password: Pass the password that is entered by the user
        :param hashed_password: Verify the password
        :return: A boolean value, true or false
        :doc-author: SergiyRus1974
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
        The hash is generated using the pwd_context object, which is an instance of Flask-Bcrypt's Bcrypt class.

        :param self: Represent the instance of the class
        :param password: str: Specify the password that will be hashed
        :return: A hashed version of the password
        :doc-author: SergiyRus1974
        """
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token.
            Args:
                data (dict): A dictionary containing the claims to be encoded in the JWT.
                expires_delta (Optional[float]): An optional parameter specifying how long, in seconds,
                the access token should last before expiring. If not specified, it defaults to 15 minutes.

        :param self: Access the class attributes and methods
        :param data: dict: Pass in the data that you want to encode into your token
        :param expires_delta: Optional[float]: Set the expiration time of the access token
        :return: A token that is encoded with the user's id and email
        :doc-author: SergiyRus1974
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The number of seconds until the refresh token expires. Defaults to None, which sets it to 7 days from now.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the user's data, which is then encoded into a jwt
        :param expires_delta: Optional[float]: Set the expiration time of the refresh token
        :return: A refresh token
        :doc-author: SergiyRus1974
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function takes a refresh token and decodes it.
            If the scope is not 'refresh_token', then an HTTPException is raised.
            If the JWTError exception occurs, then an HTTPException is raised.

        :param self: Represent the instance of a class
        :param refresh_token: str: Pass in the refresh token that is sent from the client
        :return: The email of the user who has sent the refresh token
        :doc-author: SergiyRus1974
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            print(payload['scope'])
            if payload['scope'] == 'refresh_token':
                email = payload.get("sub")
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be used in the
            protected endpoints. It takes a token as an argument and returns the user
            associated with that token. If no user is found, it raises an exception.

        :param self: Access the class attributes
        :param token: str: Pass the token that is sent in the authorization header
        :param db: AsyncSession: Create a database session
        :return: The user object associated with the email in the jwt payload
        :doc-author: SergiyRus1974
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception

            email = payload["sub"]
            if email is None:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repositories_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception

        if user.refresh_token is None:
            raise credentials_exception
        return user

    async def create_email_token(self, data: dict):
        """
        The create_email_token function takes in a dictionary of data and returns a token.
        The function creates an expiration date for the token, adds it to the dictionary,
        and then encodes it using jwt.

        :param self: Represent the instance of the class
        :param data: dict: Create the token
        :return: A token which is a string
        :doc-author: SergiyRus1974
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email associated with that token.
        It does this by decoding the JWT using our secret key and algorithm, then returning the subject (sub) field of
        the payload.

        :param self: Represent the instance of the class
        :param token: str: Pass in the token that was sent to the user's email
        :return: The email from the token
        :doc-author: SergiyRus1974
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
