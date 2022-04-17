from fastapi import Depends, HTTPException
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette import status

import tables
from database import get_session
from log_conf import logger_wraps

from models.products import (
    ProductCreate,
    ProductUpdate,
    ProductBuy
)

logger = logging.getLogger("warehouse")


class DBService:

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    @logger_wraps
    def _get_product(self, product_id: int) -> tables.Product:
        product = self.session.query(tables.Product).get(product_id)
        if product:
            return product

        logger.info("404 Not Found: Product not found")
        raise HTTPException(status_code=404, detail="Product not found")

    @logger_wraps
    def get_product(self, product_id: int) -> tables.Product:
        product = self._get_product(product_id)
        if product.quantity > 0:
            logger.info(f"OK return -> {product.asdict()}")
            return product

        logger.info("404 Not Found: Quantity == 0")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    @logger_wraps
    def create_product(self, user_id: int, product_data: ProductCreate) -> tables.Product:
        product = tables.Product(**product_data.dict(), user_id=user_id)
        try:
            self.session.add(product)
            self.session.commit()
            logger.info(f"OK: created -> {product.asdict()}")
            return product
        except IntegrityError:
            logger.info("400 Bad Request: Product is already added")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is already added"
            )

    @logger_wraps
    def update_product(self, product_id: int, user_id: int, product_data: ProductUpdate) -> tables.Product:
        product = self._get_product(product_id)
        if product.user_id == user_id:
            try:
                for field, value in product_data:
                    setattr(product, field, value)
                self.session.commit()
                logger.info(f"OK: updated -> {product.asdict()}")
                return product
            except IntegrityError:
                logger.info("400 Bad Request: Product already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product already exists"
                )
        else:
            logger.info("403 Forbidden: Updating product is forbidden")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Updating product is forbidden"
            )

    @logger_wraps
    def delete_product(self, product_id: int, user_id: int):
        product = self._get_product(product_id)
        if product.user_id == user_id:
            self.session.delete(product)
            self.session.commit()
            logger.info(f"OK: deleted -> {product.asdict()}")
        else:
            logger.info("403 Forbidden: Deleting product is forbidden")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Deleting product is forbidden"
            )

    @logger_wraps
    def decrease_product(self, product_id: int, product_data: ProductBuy) -> tables.Product:
        product = self._get_product(product_id)
        left_in_stock = product.quantity - product_data.quantity
        if left_in_stock >= 0:
            ordered_product = product.asdict()
            ordered_product["quantity"] = product_data.quantity
            setattr(product, "quantity", left_in_stock)
            self.session.commit()
            logger.info(f"OK: quantity reduced -> {product.asdict()}")
        else:
            logger.info("400 Bad Request: Quantity exceeds the remainder")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Max quantity: {left_in_stock}"
            )
        logger.info(f"OK return -> {ordered_product}")
        return ordered_product
