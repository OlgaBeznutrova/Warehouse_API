from enum import Enum

from pydantic import BaseModel


class UserCategory(str, Enum):
    buyer = "buyer"
    seller = "seller"


class UserBase(BaseModel):
    username: str
    email: str
    category: UserCategory


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
