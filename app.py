from fastapi import FastAPI, Depends
from logging.config import dictConfig

from api.products import router as product_router
from api.users import router as auth_router
from log_conf import LOGGING, get_request

dictConfig(LOGGING)
app = FastAPI(title="Warehouse_API")
app.include_router(product_router, dependencies=[Depends(get_request)])
app.include_router(auth_router, dependencies=[Depends(get_request)])
