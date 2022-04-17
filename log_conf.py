from fastapi import Request
from functools import wraps
import logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "loggers": {
        "warehouse": {
            "handlers": ["file_handler", "stream_handler"],
            "level": "DEBUG",
            "propagate": True
        },
        "uvicorn.access": {
            "handlers": ["file_handler"],
            "level": "DEBUG",
            "propagate": True
        },
        "uvicorn.error": {
            "handlers": ["file_handler"],
            "level": "DEBUG",
            "propagate": True
        }
    },

    "handlers": {
        "file_handler": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "log.log",
            "formatter": "default",
            "encoding": "utf-8"
        },
        "stream_handler": {
            "class": "logging.StreamHandler",
            "formatter": "default",

        }
    },

    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    }

}

logger = logging.getLogger("warehouse")


# logging urls (DI for app.py)
def get_request(request: Request):
    logger.info(f"{request.method} {request.url}")
    logger.info(f"Client: {request.client}")
    logger.debug("Params:")
    for param, param_value in request.path_params.items():
        logger.debug(f"\t{param}: {param_value}")
    logger.debug(f"Endpoint: {request.scope['endpoint']}")


# decorator for logging functions Entering and Exiting
def logger_wraps(func):
    name = func.__name__

    @wraps(func)
    def wrapped(*args, **kwargs):
        logger.debug(f"Entering {name} (args={args}, kwargs={kwargs})")
        result = func(*args, **kwargs)
        logger.debug(f"Exiting {name} (result={result})")
        return result

    return wrapped
