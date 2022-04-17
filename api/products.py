from fastapi import APIRouter, HTTPException
from fastapi import Depends
import logging
from starlette import status
from starlette.responses import Response

from log_conf import logger_wraps
from models.auth import User
from models.products import (
    ProductOut,
    ProductCreate,
    ProductUpdate,
    ProductBuy
)
from services.user_service import get_current_user
from services.db_service import DBService

logger = logging.getLogger("warehouse")
router = APIRouter(prefix="/products", tags=["products"])


@logger_wraps
@router.get("/{product_id}", response_model=ProductOut)
def display_product(
        product_id: int,
        dbservice: DBService = Depends(),
):
    return dbservice.get_product(product_id)


@logger_wraps
@router.post("/add", response_model=ProductOut)
def add_product(
        product_data: ProductCreate,
        user: User = Depends(get_current_user),
        dbservice: DBService = Depends()
):
    if user.category == "seller":
        return dbservice.create_product(user.id, product_data)
    else:
        logger.info("403 Forbidden: Adding product is forbidden")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Adding product is forbidden"
        )


@logger_wraps
@router.put("/{product_id}", response_model=ProductOut)
def update_existing_product(
        product_id: int,
        product_data: ProductUpdate,
        user: User = Depends(get_current_user),
        dbservice: DBService = Depends()
):
    if user.category == "seller":
        return dbservice.update_product(product_id, user.id, product_data)
    else:
        logger.info("403 Forbidden: Updating product is forbidden")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Updating product is forbidden"
        )


@logger_wraps
@router.delete("/{product_id}")
def delete_existing_product(
        product_id: int,
        user: User = Depends(get_current_user),
        dbservice: DBService = Depends()
):
    if user.category == "seller":
        dbservice.delete_product(product_id, user.id)
        return Response(status_code=status.HTTP_202_ACCEPTED)
    else:
        logger.info("403 Forbidden: Deleting product is forbidden")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Deleting product is forbidden"
        )


@logger_wraps
@router.post("/buy/{product_id}", response_model=ProductOut)
def buy_product(
        product_id: int,
        product_data: ProductBuy,
        user: User = Depends(get_current_user),
        dbservice: DBService = Depends()

):
    if user.category == "buyer":
        return dbservice.decrease_product(product_id, product_data)
    else:
        logger.info("403 Forbidden: Buying product is forbidden")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Buying product is forbidden"
        )
