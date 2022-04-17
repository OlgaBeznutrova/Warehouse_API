import logging

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from log_conf import logger_wraps
from models.auth import User, UserCreate, Token
from services.user_service import AuthService, get_current_user, oauth2_scheme

router = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger("warehouse")


# register new user
@logger_wraps
@router.post("/sign-up", response_model=Token)
def sing_up(
        user_data: UserCreate,
        auth_service: AuthService = Depends()
):
    return auth_service.register_new_user(user_data)


# user sign in
@logger_wraps
@router.post("/sign-in", response_model=Token)
def sign_in(
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthService = Depends()
):
    return auth_service.authenticate_user(
        form_data.username,
        form_data.password
    )


# display user
@logger_wraps
@router.get("/user", response_model=User)
def get_user(user: User = Depends(get_current_user)):
    return user
