from datetime import datetime, timedelta
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from passlib.hash import bcrypt
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import tables
from database import get_session
from log_conf import logger_wraps
from models.auth import User, Token, UserCreate
from settings import settings

logger = logging.getLogger("warehouse")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/sign-in")


@logger_wraps
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return AuthService.validate_token(token)


class AuthService:

    # get hashed password
    @classmethod
    @logger_wraps
    def get_password_hash(cls, password: str) -> str:
        return bcrypt.hash(password)

    # verify user's password
    @classmethod
    @logger_wraps
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    # create user token
    @classmethod
    @logger_wraps
    def create_token(cls, user: tables.User) -> Token:
        now = datetime.utcnow()
        payload = {
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(seconds=settings.jwt_expiration),
            "sub": str(user.id),
            "user": user.asdict()
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            settings.jwt_algorithm
        )

        return Token(access_token=token)

    # validate token from query
    @classmethod
    @logger_wraps
    def validate_token(cls, token: str) -> User:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )
        except JWTError:
            logger.info("401 Unauthorized: Could not validate credentials")
            raise exception
        user_data = payload.get("user")
        try:
            user = User.parse_obj(user_data)
        except ValidationError:
            logger.info("401 Unauthorized: Could not validate credentials")
            raise exception
        return user

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    # add new user into database
    @logger_wraps
    def register_new_user(self, user_data: UserCreate) -> Token:
        user = tables.User(
            username=user_data.username,
            email=user_data.email,
            category=user_data.category,
            password_hash=self.get_password_hash(user_data.password)

        )
        try:
            self.session.add(user)
            self.session.commit()
            return self.create_token(user)

        except IntegrityError:
            logger.info("400 Bad Request: User with this name or email already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this name or email already exists"
            )

    # authenticate user by username and password
    @logger_wraps
    def authenticate_user(self, username: str, password: str) -> Token:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        user = self.session.query(tables.User).filter(tables.User.username == username).first()
        if not user:
            logger.info("401 Unauthorized: Incorrect username or password")
            raise exception
        if not self.verify_password(password, user.password_hash):
            logger.info("401 Unauthorized: Incorrect username or password")
            raise exception

        return self.create_token(user)
