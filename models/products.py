from decimal import Decimal
from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    title: str
    price: Decimal
    quantity: int
    description: Optional[str] = None


class ProductOut(ProductBase):
    id: int
    user_id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductBuy(BaseModel):
    quantity: int
